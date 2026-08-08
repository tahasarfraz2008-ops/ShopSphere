from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class User(AbstractUser):
    """
    Users table.
    Extends Django's built-in auth user with e-commerce specific fields.
    """
    email = models.EmailField(unique=True, null=False, blank=False)
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    date_joined = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Category(models.Model):
    """Categories table."""
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, null=False)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Products table."""
    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=False)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False,
                                 validators=[MinValueValidator(0)])
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                  related_name='products', null=True)
    image_url = models.CharField(max_length=500, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category', 'price']),
            models.Index(fields=['stock_quantity']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_out_of_stock(self):
        return self.stock_quantity <= 0

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(avg=models.Avg('rating'))
        return round(agg['avg'], 1) if agg['avg'] else 0


class Order(models.Model):
    """Orders table."""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=False)
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_address = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['user', 'order_date']),
        ]
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.order_id} - {self.user.username}"


class OrderItem(models.Model):
    """Order_Items table."""
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', null=False)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.quantity * self.price


class Payment(models.Model):
    """Payments table."""
    METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('PayPal', 'PayPal'),
        ('Cash on Delivery', 'Cash on Delivery'),
        ('Bank Transfer', 'Bank Transfer'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', null=False)
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=False)
    payment_method = models.CharField(max_length=30, choices=METHOD_CHOICES, default='Credit Card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed')

    class Meta:
        indexes = [
            models.Index(fields=['payment_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment #{self.payment_id} for Order #{self.order.order_id}"


class Review(models.Model):
    """Reviews table."""
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', null=False)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_review_per_user_product'),
        ]
        indexes = [
            models.Index(fields=['product', 'rating']),
        ]

    def __str__(self):
        return f"{self.rating}* review by {self.user.username} on {self.product.name}"
