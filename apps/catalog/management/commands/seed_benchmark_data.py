"""Seed deterministic benchmark data.

This command is idempotent and reproducible: same args -> same data. That
matters because two benchmark runs on different datasets are not
comparable.
"""

from __future__ import annotations

import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from apps.catalog.models import Category, Product
from apps.users.models import Role


class Command(BaseCommand):
    help = "Seed deterministic users, categories and products for benchmarking."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=1000)
        parser.add_argument("--products", type=int, default=5000)
        parser.add_argument("--categories", type=int, default=20)
        parser.add_argument("--seed", type=int, default=42)
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Wipe seeded benchmark data first (does not touch real users).",
        )

    def handle(self, *args, **opts):
        random.seed(opts["seed"])
        fake = Faker()
        Faker.seed(opts["seed"])

        if opts["reset"]:
            self.stdout.write("Resetting benchmark data...")
            Product.objects.filter(sku__startswith="BENCH-").delete()
            Category.objects.filter(slug__startswith="bench-").delete()
            get_user_model().objects.filter(email__endswith="@bench.example").delete()

        with transaction.atomic():
            categories = self._seed_categories(opts["categories"])
            self._seed_users(opts["users"], fake)
            self._seed_products(opts["products"], categories, fake)

        self.stdout.write(self.style.SUCCESS("Benchmark seed complete."))

    def _seed_categories(self, n: int) -> list[Category]:
        out: list[Category] = []
        for i in range(n):
            slug = f"bench-cat-{i:03d}"
            obj, _ = Category.objects.get_or_create(slug=slug, defaults={"name": f"Bench Cat {i}"})
            out.append(obj)
        return out

    def _seed_users(self, n: int, fake: Faker) -> None:
        User = get_user_model()
        existing = set(User.objects.filter(email__endswith="@bench.example").values_list("email", flat=True))
        bulk: list[User] = []
        for i in range(n):
            email = f"bench{i:06d}@bench.example"
            if email in existing:
                continue
            user = User(
                email=email,
                username=f"bench{i:06d}",
                role=Role.STAFF if i % 50 == 0 else Role.CUSTOMER,
            )
            user.set_password("benchpass")
            bulk.append(user)
        User.objects.bulk_create(bulk, batch_size=500, ignore_conflicts=True)
        self.stdout.write(f"Users: ensured {n} (created {len(bulk)})")

    def _seed_products(self, n: int, categories: list[Category], fake: Faker) -> None:
        existing = set(
            Product.objects.filter(sku__startswith="BENCH-").values_list("sku", flat=True)
        )
        bulk: list[Product] = []
        for i in range(n):
            sku = f"BENCH-{i:08d}"
            if sku in existing:
                continue
            cat = categories[i % len(categories)]
            bulk.append(
                Product(
                    sku=sku,
                    name=f"Product {i}",
                    slug=f"bench-prod-{i:08d}",
                    description=fake.paragraph(nb_sentences=3),
                    price=Decimal(str(round(random.uniform(2, 999), 2))),
                    stock=random.randint(0, 500),
                    is_active=True,
                    category=cat,
                )
            )
        Product.objects.bulk_create(bulk, batch_size=500, ignore_conflicts=True)
        self.stdout.write(f"Products: ensured {n} (created {len(bulk)})")
