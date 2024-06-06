from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Photo, UserRole
from .models import Product
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings


User = get_user_model()


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "product", "image", "status"]


class UserProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class ProductSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    user = UserProductSerializer(required=False)

    class Meta:
        model = Product
        fields = "__all__"


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
        }

    def create(self, validated_data):
        role = validated_data.get("role", UserRole.CUSTOMER)
        if role not in [UserRole.SELLER, UserRole.CUSTOMER]:
            raise serializers.ValidationError(
                "Invalid role. Allowed roles are 'seller' and 'customer'."
            )

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get(
                "role", UserRole.CUSTOMER
            ),  # Use default role if not provided
        )
        return user

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data["access"] = str(refresh.access_token)

        # Add extra responses here
        data["role"] = self.user.role
        data["id"] = self.user.id
        data["username"] = self.user.username
        data["email"] = self.user.email
        return data
