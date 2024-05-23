from django.urls import path
from .views import (
    CreateProductView,
    CustomTokenObtainPairView,
    LogoutView,
    UserRegistrationView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create-product/", CreateProductView.as_view(), name="create-product"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
]
