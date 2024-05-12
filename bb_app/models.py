from django.db import models
from django.contrib.auth.models import AbstractUser


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    SELLER = "SELLER", "Seller"
    CUSTOMER = "CUSTOMER", "Customer"


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=10, choices=UserRole.choices, default=UserRole.CUSTOMER
    )
