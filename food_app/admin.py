from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem

# Custom admin class for displaying purchased items inline on the Order page
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Don't show extra empty forms
    readonly_fields = ('menu_item', 'quantity', 'price') # Items shouldn't be edited once ordered
    can_delete = False

# Custom admin class for the Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone_number', 'user__username')
    list_editable = ('status',) # Allows quick status changes on the list view
    inlines = [OrderItemInline] # Show the order items immediately
    readonly_fields = ('user', 'total_price', 'created_at', 'updated_at') # These fields are set by the system

# Custom admin class for Menu Items
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    list_editable = ('price', 'is_available')

# Register other models
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}