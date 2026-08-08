import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from store.models import User, Category, Product, Order, OrderItem, Payment, Review

fake = Faker()

CATEGORY_NAMES = [
    "Electronics", "Clothing & Apparel", "Home & Kitchen", "Books",
    "Sports & Outdoors", "Beauty & Personal Care", "Toys & Games",
    "Automotive", "Grocery", "Health & Wellness",
]

PRODUCT_ADJECTIVES = ["Premium", "Deluxe", "Compact", "Wireless", "Portable",
                      "Classic", "Pro", "Eco-Friendly", "Smart", "Ultra"]
PRODUCT_NOUNS = ["Headphones", "Blender", "Backpack", "Sneakers", "Watch",
                 "Lamp", "Notebook", "Jacket", "Speaker", "Bottle",
                 "Chair", "Camera", "Mug", "Charger", "Keyboard",
                 "Monitor", "Sofa", "Sunglasses", "Wallet", "Tent"]

PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'PayPal', 'Cash on Delivery', 'Bank Transfer']
ORDER_STATUSES = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']


class Command(BaseCommand):
    help = "Seed the database with realistic sample data matching the project spec volumes."

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete existing data before seeding.')

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Flushing existing data...')
            Review.objects.all().delete()
            Payment.objects.all().delete()
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        with transaction.atomic():
            categories = self.seed_categories()
            users = self.seed_users(100)
            products = self.seed_products(200, categories)
            orders = self.seed_orders(500, users)
            self.seed_order_items(1000, orders, products)
            self.seed_payments(orders)
            self.seed_reviews(300, users, products)

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {Category.objects.count()} categories, "
            f"{User.objects.count()} users, {Product.objects.count()} products, "
            f"{Order.objects.count()} orders, {OrderItem.objects.count()} order items, "
            f"{Payment.objects.count()} payments, {Review.objects.count()} reviews."
        ))

    def seed_categories(self):
        self.stdout.write('Seeding categories...')
        cats = []
        for name in CATEGORY_NAMES:
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={'description': fake.sentence(nb_words=10)}
            )
            cats.append(cat)
        return cats

    def seed_users(self, count):
        self.stdout.write(f'Seeding {count} users...')
        users = []
        used_usernames = set(User.objects.values_list('username', flat=True))
        for i in range(count):
            first = fake.first_name()
            last = fake.last_name()
            username = f"{first.lower()}.{last.lower()}{random.randint(1,999)}"
            if username in used_usernames:
                username = f"{username}_{i}"
            used_usernames.add(username)
            user = User(
                username=username,
                first_name=first,
                last_name=last,
                email=f"{username}@example.com",
                phone=fake.phone_number()[:20],
                address=fake.street_address(),
                city=fake.city(),
                country=fake.country(),
                date_joined=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone()),
                is_verified=random.choice([True, True, False]),
            )
            user.set_password('Password123!')
            users.append(user)
        User.objects.bulk_create(users, batch_size=200)
        return list(User.objects.filter(is_superuser=False))

    def seed_products(self, count, categories):
        self.stdout.write(f'Seeding {count} products...')
        products = []
        for _ in range(count):
            adj = random.choice(PRODUCT_ADJECTIVES)
            noun = random.choice(PRODUCT_NOUNS)
            name = f"{adj} {noun} {fake.word().capitalize()}"
            stock = random.choices([0, random.randint(1, 200)], weights=[10, 90])[0]
            products.append(Product(
                name=name,
                description=fake.paragraph(nb_sentences=3),
                price=Decimal(random.randrange(500, 50000)) / 100,
                stock_quantity=stock,
                category=random.choice(categories),
                image_url='',
                is_active=True,
                created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
            ))
        Product.objects.bulk_create(products, batch_size=200)
        return list(Product.objects.all())

    def seed_orders(self, count, users):
        self.stdout.write(f'Seeding {count} orders...')
        orders = []
        for _ in range(count):
            orders.append(Order(
                user=random.choice(users),
                order_date=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
                status=random.choice(ORDER_STATUSES),
                total_amount=Decimal('0.00'),
                shipping_address=fake.street_address(),
            ))
        Order.objects.bulk_create(orders, batch_size=200)
        return list(Order.objects.all())

    def seed_order_items(self, count, orders, products):
        self.stdout.write(f'Seeding {count} order items...')
        items = []
        order_totals = {order.order_id: Decimal('0.00') for order in orders}

        # Guarantee every order gets at least one item first
        for order in orders:
            product = random.choice(products)
            qty = random.randint(1, 5)
            items.append(OrderItem(order=order, product=product, quantity=qty, price=product.price))
            order_totals[order.order_id] += product.price * qty

        remaining = max(count - len(orders), 0)
        for _ in range(remaining):
            order = random.choice(orders)
            product = random.choice(products)
            qty = random.randint(1, 5)
            items.append(OrderItem(order=order, product=product, quantity=qty, price=product.price))
            order_totals[order.order_id] += product.price * qty

        OrderItem.objects.bulk_create(items, batch_size=300)

        # Update order totals to match their items
        for order in orders:
            order.total_amount = order_totals[order.order_id]
        Order.objects.bulk_update(orders, ['total_amount'], batch_size=200)

    def seed_payments(self, orders):
        self.stdout.write(f'Seeding payments for {min(len(orders), 500)} orders...')
        payments = []
        chosen_orders = orders if len(orders) <= 500 else random.sample(orders, 500)
        for order in chosen_orders:
            status = 'Completed' if order.status in ('Delivered', 'Shipped', 'Processing') else random.choice(['Pending', 'Completed', 'Failed'])
            payments.append(Payment(
                order=order,
                payment_date=order.order_date,
                amount=order.total_amount,
                payment_method=random.choice(PAYMENT_METHODS),
                status=status,
            ))
        Payment.objects.bulk_create(payments, batch_size=200)

    def seed_reviews(self, count, users, products):
        self.stdout.write(f'Seeding {count} reviews...')
        reviews = []
        seen_pairs = set()
        attempts = 0
        while len(reviews) < count and attempts < count * 5:
            attempts += 1
            user = random.choice(users)
            product = random.choice(products)
            pair = (user.id, product.product_id)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            reviews.append(Review(
                user=user,
                product=product,
                rating=random.choices([1, 2, 3, 4, 5], weights=[5, 8, 17, 35, 35])[0],
                comment=fake.sentence(nb_words=15),
                created_at=fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.get_current_timezone()),
            ))
        Review.objects.bulk_create(reviews, batch_size=200)
