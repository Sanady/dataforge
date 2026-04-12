"""Compatibility layer — drop-in replacements for other fake data libraries.

Usage::

    from dataforge.compat import Faker

    fake = Faker("en_US")
    fake.name()          # "James Smith"
    fake.email()         # "james.smith@gmail.com"
    fake.seed_instance(42)
"""

from dataforge.compat.faker import Faker

__all__ = ["Faker"]
