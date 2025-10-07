from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Customer Menu/Home
    path('', views.menu_list, name='menu_list'),

    # Cart Management
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout & Confirmation
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<int:order_id>/', views.confirmation, name='confirmation'),
    
    # Customer History (Requires login)
    path('orders/history/', login_required(views.order_history), name='order_history'),

    # Restaurant Dashboard (Requires staff status)
    path('orders/restaurant/dashboard/', views.dashboard_view, name='dashboard'),
]