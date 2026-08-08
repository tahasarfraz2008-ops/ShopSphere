<<<<<<< HEAD
# ShopSphere — E-Commerce Management System (Django + MySQL/XAMPP)

A full-stack Django implementation of the Database Project spec: a 7-table
relational schema on **MySQL (via XAMPP)**, seeded sample data at the exact
required volumes, CRUD, analytics queries, indexing, and query optimization —
plus a complete storefront UI with authentication.

## 1. Set up MySQL in XAMPP

1. Open the **XAMPP Control Panel** and start **Apache** and **MySQL**.
2. Go to `http://localhost/phpmyadmin`.
3. Click **New**, create a database named `shopsphere_db`, collation
   `utf8mb4_unicode_ci`. (You don't need to add tables by hand — Django's
   migrations build the schema for you in step 3 below. If you'd rather see
   the raw SQL run directly, `sql/01_schema.sql` creates the same database
   and tables from the phpMyAdmin **SQL** tab or the `mysql` CLI.)
4. XAMPP's default MySQL account is `root` with an **empty password** on
   port `3306` — that's what `ecommerce_project/settings.py` assumes. If your
   setup differs, override it with environment variables (see below) instead
   of editing `settings.py` directly:

   | Variable | Default |
   |---|---|
   | `DB_NAME` | `shopsphere_db` |
   | `DB_USER` | `root` |
   | `DB_PASSWORD` | *(empty)* |
   | `DB_HOST` | `127.0.0.1` |
   | `DB_PORT` | `3306` |

## 2. Install & run

```bash
# 1. Install dependencies
pip install -r requirements.txt
# Windows note: if `mysqlclient` fails to build, see the comment at the
# bottom of requirements.txt for a pymysql-based alternative.

# 2. Build the schema (creates all 7 tables + indexes/constraints in MySQL)
python manage.py migrate

# 3. Seed realistic sample data at the required volumes
python manage.py seed_data

# 4. Create an admin account for /admin/
python manage.py createsuperuser

# 5. Run the server
python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Login Credentials (after seeding)

**Sample seeded customer accounts** (all seeded users share this password):
- Password: `Password123!`
- Any username from the database works, e.g.:
  ```bash
  python manage.py shell -c "from store.models import User; print(User.objects.filter(is_superuser=False).first().username)"
  ```

## What's Included (mapped to the project phases)

| Phase | Where it lives |
|---|---|
| **Phase 1 — Schema** | `store/models.py` (Django ORM, builds MySQL tables via `migrate`) **and** `sql/01_schema.sql` (equivalent raw MySQL DDL) — all 7 tables with PKs, FKs, `NOT NULL`, `UNIQUE`, `DEFAULT` and `CHECK` constraints |
| **Phase 2 — Sample Data** | `store/management/commands/seed_data.py` generates 100 Users, 200 Products, 10 Categories, 500 Orders, 1,000 Order_Items, 500 Payments, 300 Reviews with Faker; `sql/02_sample_data.sql` shows the same shape as plain `INSERT`s |
| **Phase 3 — CRUD** | App: signup/`profile`/checkout/admin pages. Raw SQL: `sql/03_crud_operations.sql` |
| **Phase 4 — Queries** | App: `store/views.py::dashboard_view` (ORM aggregates). Raw SQL: `sql/04_queries.sql` — all 5 basic + 5 intermediate queries |
| **Phase 5 — Indexing** | `Meta.indexes` in `models.py` (email/name/order_date plus composite indexes for real query patterns). Raw SQL walkthrough with `EXPLAIN` before/after: `sql/05_indexing.sql` |
| **Phase 6 — Optimization** | Views use `select_related`/`prefetch_related`, never `SELECT *`. Two fully worked slow-query rewrites with `EXPLAIN` before/after: `sql/06_optimization.sql` |

## App Structure

```
ecommerce_project/
├── ecommerce_project/       # Django project settings & URLs (MySQL config)
├── store/                   # Main app
│   ├── models.py            # The 7 database tables, indexes, constraints
│   ├── views.py             # All page logic (auth, catalog, cart, orders, dashboard)
│   ├── forms.py             # Signup form + review form
│   ├── admin.py             # Django admin registrations (CRUD UI for every table)
│   ├── urls.py
│   └── management/commands/seed_data.py   # Data generator
├── templates/store/         # All HTML pages
├── static/css/style.css     # Custom design system (no framework/Bootstrap)
├── static/js/main.js        # Password strength meter, toggles, alert auto-dismiss
├── sql/                     # Standalone raw SQL for every project phase
│   ├── 01_schema.sql
│   ├── 02_sample_data.sql
│   ├── 03_crud_operations.sql
│   ├── 04_queries.sql
│   ├── 05_indexing.sql
│   └── 06_optimization.sql
└── requirements.txt
```

## Design

The storefront uses a custom "night-market ledger" design system (no
Bootstrap/Tailwind): an ink-navy header/footer, warm paper surfaces, an amber
accent, and product prices styled as hang-tags. Fonts: **Fraunces** (display)
+ **Public Sans** (body/UI), loaded from Google Fonts in `base.html`. All
colors and spacing are CSS variables at the top of `static/css/style.css`, so
re-theming is a one-file change.

## Pages

- `/` — Product catalog with search, category filter, stock filter, sorting, pagination
- `/product/<id>/` — Product detail, reviews, add-to-cart
- `/cart/` — Session-based shopping cart
- `/checkout/` — Places a real Order + Order_Items + Payment
- `/orders/` and `/orders/<id>/` — Customer order history
- `/signup/`, `/login/`, `/logout/` — Auth with password strength meter & validation
- `/profile/` — Edit account details
- `/dashboard/` — Live analytics from Phase 4 queries
- `/admin/` — Full Django admin CRUD for every table

## Notes

- To inspect the raw SQL Django generates for any ORM query:
  ```python
  python manage.py shell
  >>> from store.models import Order
  >>> print(Order.objects.filter(status='Delivered').query)
  ```
- To run `EXPLAIN` on an ORM queryset directly:
  ```python
  print(Product.objects.filter(name__icontains='Pro').explain())
  ```
- `SECRET_KEY` in `settings.py` is a development placeholder — replace it
  before deploying this anywhere public, and set `DEBUG = False`.
=======
# ShopSphere
>>>>>>> d36c3311fdc1b4a14459a33325f65bde031e9269
