from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, Order, OrderItem, Payment, Review


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'city', 'is_verified', 'date_joined')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('E-Commerce Info', {'fields': ('phone', 'address', 'city', 'country', 'is_verified')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name', 'created_at')
    search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'category', 'price', 'stock_quantity', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'order_date', 'status', 'total_amount')
    list_filter = ('status',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_item_id', 'order', 'product', 'quantity', 'price')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'amount', 'payment_method', 'status', 'payment_date')
    list_filter = ('payment_method', 'status')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'user', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
