from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    SELLER = "SELLER", "Seller"
    CUSTOMER = "CUSTOMER", "Customer"


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=10, choices=UserRole.choices, default=UserRole.CUSTOMER
    )


class Product(models.Model):
    code = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    stock = models.IntegerField()
    revenue = models.FloatField()
    user_id = models.UUIDField()

    def __str__(self):
        return self.name


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="photos"
    )
    url = models.URLField(max_length=200)
    status = models.CharField(max_length=100)

    def __str__(self):
        return f"Photo {self.id} of Product {self.product.code}"
