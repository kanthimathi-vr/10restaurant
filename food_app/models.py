from django.db import models
from django.contrib.auth.models import User

# Menu Structure
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.price})"

# Order Structure
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('READY', 'Ready for Pickup/Delivery'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    # If the user is logged in, link to them. Null=True allows guest orders.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Customer details (for guest or contact)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    
    # Order details
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} - {self.name} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2) # Price at time of purchase

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"