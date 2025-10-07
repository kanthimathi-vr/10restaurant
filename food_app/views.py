from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import user_passes_test, login_required # <-- FIX HERE
from decimal import Decimal

from .models import MenuItem, Category, Order, OrderItem
from .forms import CheckoutForm

# --- Utility Functions ---

def is_staff_or_superuser(user):
    """Custom test to check if user has access to the dashboard."""
    return user.is_active and (user.is_staff or user.is_superuser)

def get_cart(request):
    """Retrieves the cart dictionary from the session."""
    return request.session.get('cart', {})

def save_cart(request, cart):
    """Saves the cart dictionary back to the session."""
    request.session['cart'] = cart
    request.session.modified = True

# --- Customer Views ---

def menu_list(request):
    """Displays the main menu, categorized."""
    categories = Category.objects.filter(is_active=True).order_by('id')
    
    # Pre-fetch menu items to reduce queries
    menu_items = MenuItem.objects.filter(
        is_available=True, 
        category__is_active=True
    ).select_related('category')
    
    # Group items by category
    categorized_menu = {}
    for category in categories:
        categorized_menu[category] = [item for item in menu_items if item.category_id == category.id]

    # Get cart count for display in template
    cart = get_cart(request)
    cart_count = sum(item['quantity'] for item in cart.values())
    
    context = {
        'categorized_menu': categorized_menu,
        'cart_count': cart_count,
    }
    return render(request, 'menu.html', context)

def add_to_cart(request, item_id):
    """Adds a menu item to the session cart."""
    menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    cart = get_cart(request)

    # Convert item_id to string as session keys are strings
    item_key = str(item_id)

    if item_key in cart:
        cart[item_key]['quantity'] += 1
        messages.success(request, f"Added another {menu_item.name} to your cart.")
    else:
        cart[item_key] = {
            'id': menu_item.id,
            'name': menu_item.name,
            'price': float(menu_item.price), # Store as float/int for JSON serialization
            'quantity': 1,
        }
        messages.success(request, f"Added {menu_item.name} to your cart.")

    save_cart(request, cart)
    return redirect('menu_list') # Redirect back to the menu

def remove_from_cart(request, item_id):
    """Removes a single instance of an item from the cart, or removes the item entirely if quantity is 1."""
    cart = get_cart(request)
    item_key = str(item_id)
    
    if item_key in cart:
        if cart[item_key]['quantity'] > 1:
            cart[item_key]['quantity'] -= 1
            messages.warning(request, f"Removed one instance of {cart[item_key]['name']}.")
        else:
            del cart[item_key]
            messages.error(request, f"Removed the last {cart[item_key]['name']} entirely from your cart.")
        
        save_cart(request, cart)
    
    return redirect('view_cart')

def view_cart(request):
    """Displays the current contents of the shopping cart."""
    cart = get_cart(request)
    cart_items = []
    subtotal = Decimal('0.00')

    for item_key, data in cart.items():
        price = Decimal(str(data['price']))
        total_item_price = price * data['quantity']
        subtotal += total_item_price
        
        cart_items.append({
            'id': data['id'],
            'name': data['name'],
            'price': price,
            'quantity': data['quantity'],
            'total_item_price': total_item_price,
        })
        
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'cart_count': sum(item['quantity'] for item in cart.values()),
    }
    return render(request, 'cart.html', context)

def checkout(request):
    """Handles the final steps of placing an order (simulated payment)."""
    cart = get_cart(request)
    if not cart:
        messages.warning(request, "Your cart is empty. Please add items to order.")
        return redirect('menu_list')

    # Calculate total price
    total_price = Decimal('0.00')
    for item_data in cart.values():
        total_price += Decimal(str(item_data['price'])) * item_data['quantity']

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone_number = form.cleaned_data['phone_number']

            # --- Transactional Order Processing (Simulated Payment) ---
            try:
                with transaction.atomic():
                    # 1. Create the main Order object
                    order = Order.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        name=name,
                        phone_number=phone_number,
                        total_price=total_price,
                        status='PENDING' 
                    )

                    # 2. Create OrderItem objects from the cart
                    # Using get_objects_or_404 to ensure items still exist
                    menu_item_ids = [item['id'] for item in cart.values()]
                    menu_items = MenuItem.objects.in_bulk(menu_item_ids)

                    for item_data in cart.values():
                        item_id = item_data['id']
                        
                        OrderItem.objects.create(
                            order=order,
                            menu_item=menu_items.get(item_id), # Use .get() in case the item was deleted
                            quantity=item_data['quantity'],
                            price=Decimal(str(item_data['price']))
                        )

                    # 3. Clear the session cart on successful order
                    request.session['cart'] = {}
                    request.session.modified = True
                    
                    messages.success(request, f"Order #{order.id} placed successfully! We are preparing it now.")
                    return redirect('confirmation', order_id=order.id)

            except Exception as e:
                messages.error(request, "There was an error processing your order. Please try again.")
                # Log the error in a real application
                print(f"Order Processing Error: {e}")
    else:
        # Pre-populate form if user is logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'phone_number': '', 
            }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'total_price': total_price,
        'cart_count': sum(item['quantity'] for item in cart.values()),
    }
    return render(request, 'checkout.html', context)

def confirmation(request, order_id):
    """Order confirmation page after successful checkout."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'confirmation.html', {'order': order})

@login_required
def order_history(request):
    """Shows the logged-in user's past orders."""
    # Only retrieve orders belonging to the current authenticated user
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items__menu_item')
    
    context = {
        'orders': orders,
    }
    return render(request, 'order_history.html', context)


# --- Restaurant Dashboard View ---

@user_passes_test(is_staff_or_superuser, login_url='/accounts/login/')
def dashboard_view(request):
    """Displays the restaurant dashboard showing pending and preparing orders."""
    
    # 1. Get Pending Orders (New)
    pending_orders = Order.objects.filter(status='PENDING').order_by('created_at').prefetch_related('items__menu_item')

    # 2. Get Orders in Preparation
    preparing_orders = Order.objects.filter(status='PREPARING').order_by('created_at').prefetch_related('items__menu_item')

    # 3. Get Completed/Cancelled Orders (for summary)
    recent_completed = Order.objects.filter(status='COMPLETED').order_by('-created_at')[:10]
    
    context = {
        'pending_orders': pending_orders,
        'preparing_orders': preparing_orders,
        'recent_completed': recent_completed,
    }
    return render(request, 'dashboard.html', context)
