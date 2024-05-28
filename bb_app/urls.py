from django.urls import path
from .views import (
    CreateProductView,
    CustomTokenObtainPairView,
    LogoutView,
    PhotoCreateView,
    PhotoUploadView,
    ProductBySellerListView,
    ProductByStatusListView,
    ProductDeleteView,
    ProductDetailView,
    ProductListView,
    ProductUpdateView,
    UserRegistrationView,
)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("create-product/", CreateProductView.as_view(), name="create-product"),
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "products/seller/<uuid:user_id>/",
        ProductBySellerListView.as_view(),
        name="products-by-seller",
    ),
    path(
        "products/status/<str:status>/",
        ProductByStatusListView.as_view(),
        name="products-by-status",
    ),
    path("products/", ProductListView.as_view(), name="product-list"),
    path(
        "product/update/<uuid:code>/",
        ProductUpdateView.as_view(),
        name="update-product",
    ),
    path("product/<uuid:code>/", ProductDetailView.as_view(), name="product-detail"),
    path(
        "product/delete/<uuid:code>/",
        ProductDeleteView.as_view(),
        name="delete-product",
    ),
    path("photos/upload/", PhotoUploadView.as_view(), name="photo-upload"),
    # path("photos/create/", PhotoCreateView.as_view(), name="create-photo"),
]
