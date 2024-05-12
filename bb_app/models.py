from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # Add any additional fields you want
    pass


# Remember to set AUTH_USER_MODEL in your settings.py to 'bb_app.CustomUser'
