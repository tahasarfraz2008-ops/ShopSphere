from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Sum, F, DecimalField
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth import get_user_model

from .forms import SignUpForm, ReviewForm
from .models import Category, Product, Order, OrderItem, Payment, Review

User = get_user_model()


# ---------- Auth ----------

class CustomLoginView(LoginView):
    template_name = 'store/login.html'
    redirect_authenticated_user = True


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome aboard, {user.first_name}! Your account is ready.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'store/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ---------- Catalog ----------

def home_view(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    stock = request.GET.get('stock', '')
    sort = request.GET.get('sort', 'newest')

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)
    if stock == 'in':
        products = products.filter(stock_quantity__gt=0)
    elif stock == 'out':
        products = products.filter(stock_quantity=0)

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'stock': stock,
        'sort': sort,
        'total_products': Product.objects.filter(is_active=True).count(),
    }
    return render(request, 'store/home.html', context)


def product_detail_view(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = product.reviews.select_related('user').all()
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]

    review_form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                messages.success(request, 'Your review has been posted.')
                return redirect('product_detail', product_id=product.pk)
        else:
            review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'related': related,
        'review_form': review_form,
    }
    return render(request, 'store/product_detail.html', context)


# ---------- Cart (session based) ----------

def _get_cart(request):
    return request.session.setdefault('cart', {})


def cart_view(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')
    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            continue
        subtotal = product.price * qty
        total += subtotal
        items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
    return render(request, 'store/cart.html', {'items': items, 'total': total})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = _get_cart(request)
    qty = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    request.session.modified = True
    messages.success(request, f'Added "{product.name}" to your cart.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
    return redirect('cart')


def update_cart(request, product_id):
    cart = _get_cart(request)
    qty = int(request.POST.get('quantity', 1))
    if qty <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = qty
    request.session.modified = True
    return redirect('cart')


@login_required
def checkout_view(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('home')

    items = []
    total = Decimal('0.00')
    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            continue
        subtotal = product.price * qty
        total += subtotal
        items.append((product, qty, subtotal))

    if request.method == 'POST':
        address = request.POST.get('shipping_address', request.user.address)
        payment_method = request.POST.get('payment_method', 'Credit Card')

        order = Order.objects.create(
            user=request.user,
            status='Pending',
            total_amount=total,
            shipping_address=address,
        )
        for product, qty, subtotal in items:
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
            product.stock_quantity = max(product.stock_quantity - qty, 0)
            product.save(update_fields=['stock_quantity'])

        Payment.objects.create(
            order=order,
            amount=total,
            payment_method=payment_method,
            status='Completed',
        )
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, f'Order #{order.order_id} placed successfully!')
        return redirect('order_detail', order_id=order.order_id)

    return render(request, 'store/checkout.html', {'items': items, 'total': total})


# ---------- Orders ----------

@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.city = request.POST.get('city', user.city)
        user.country = request.POST.get('country', user.country)
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'store/profile.html')


# ---------- Analytics dashboard (demonstrates Phase 4 intermediate queries) ----------

@login_required
def dashboard_view(request):
    top_products = (Product.objects.annotate(units_sold=Sum('order_items__quantity'))
                    .filter(units_sold__isnull=False)
                    .order_by('-units_sold')[:5])

    total_sales = Payment.objects.filter(status='Completed').aggregate(total=Sum('amount'))['total'] or 0

    top_customer = (User.objects.annotate(order_count=Count('orders'))
                     .order_by('-order_count').first())

    monthly_sales = (Order.objects.annotate(month=TruncMonth('order_date'))
                      .values('month')
                      .annotate(total=Sum('total_amount'))
                      .order_by('month'))

    top_rated = (Product.objects.annotate(avg_rating=Avg('reviews__rating'))
                 .filter(avg_rating__gt=4)
                 .order_by('-avg_rating')[:10])

    out_of_stock_count = Product.objects.filter(stock_quantity=0).count()
    total_users = User.objects.count()
    total_orders = Order.objects.count()

    monthly_sales_list = list(monthly_sales)
    max_month_total = max([m['total'] for m in monthly_sales_list], default=1) or 1
    max_units_sold = top_products[0].units_sold if top_products else 1

    context = {
        'top_products': top_products,
        'total_sales': total_sales,
        'top_customer': top_customer,
        'monthly_sales': monthly_sales_list,
        'max_month_total': max_month_total,
        'max_units_sold': max_units_sold,
        'top_rated': top_rated,
        'out_of_stock_count': out_of_stock_count,
        'total_users': total_users,
        'total_orders': total_orders,
    }
    return render(request, 'store/dashboard.html', context)
