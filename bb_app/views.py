from django.shortcuts import render
from rest_framework import generics
from .serializers import (
    CustomTokenObtainPairSerializer,
    ProductUpdateSerializer,
    User,
    UserRegistrationSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ProductSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.generics import ListAPIView, UpdateAPIView
from .models import Product
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import Photo
from .serializers import PhotoSerializer
from rest_framework.generics import CreateAPIView
import requests
from django.http import JsonResponse
from django.db.models import Prefetch


class UserRegistrationView(generics.CreateAPIView):
    authentication_classes = []  # biar dia ga merhatiin Bearer headernya

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateProductView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # check role
        if request.user.role != "SELLER":
            return Response(
                {"message": "You must be a seller to create a product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check length
        files = request.FILES.getlist("photos")
        if len(files) > 5:
            return Response(
                {"message": "You can only upload 3-5 images."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        files_payload = [("files", file) for file in files]

        # predict
        response = requests.post(
            "https://capstone-ml-app-mo5jvyk6cq-as.a.run.app/predict",
            files=files_payload,
        )
        predictions = response.json()
        non_blur_photos = [
            prediction
            for prediction in predictions
            if prediction["prediction"] != "Blur"
        ]
        number_of_passes = len(non_blur_photos)

        # check pass
        if number_of_passes >= 3:
            request.data["status"] = "ACCEPTED"
        else:
            request.data["status"] = "BANNED"
        request.data["revenue"] = 0
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            # save data
            product = serializer.save(user=request.user)
            for prediction in predictions:
                # create photo object
                file = list(
                    filter(lambda file: file.name == prediction["filename"], files)
                )[0]
                photo = Photo.objects.create(
                    product=product,
                    status=prediction["prediction"],
                )
                with file.open("rb") as f:
                    photo.image = f
                    photo.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return self.update_product(request, partial=False, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update_product(request, partial=True, *args, **kwargs)

    def update_product(self, request, partial, *args, **kwargs):
        # check role
        if request.user.role != "SELLER":
            return Response(
                {"message": "You must be a seller to update a product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(code=kwargs["code"], user=request.user)
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        files = request.FILES.getlist("photos")

        if files:
            # check length of photos
            if len(files) > 5:
                return Response(
                    {"message": "You can only upload 3-5 images."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            files_payload = [("files", file) for file in files]

            # predict
            response = requests.post(
                "https://capstone-ml-app-mo5jvyk6cq-as.a.run.app/predict",
                files=files_payload,
            )
            predictions = response.json()
            non_blur_photos = [
                prediction
                for prediction in predictions
                if prediction["prediction"] != "Blur"
            ]
            number_of_passes = len(non_blur_photos)

            # check pass
            if number_of_passes < 3:
                request.data["status"] = "BANNED"
            else:
                request.data["status"] = "ACCEPTED"

            serializer = ProductUpdateSerializer(
                product, data=request.data, partial=partial
            )
            if serializer.is_valid():
                product = serializer.save()
                Photo.objects.filter(product=product).delete()  # delete old photos
                for prediction in predictions:
                    # create new photo object
                    file = list(
                        filter(lambda file: file.name == prediction["filename"], files)
                    )[0]
                    photo = Photo.objects.create(
                        product=product,
                        status=prediction["prediction"],
                    )
                    with file.open("rb") as f:
                        photo.image = f
                        photo.save()
                return Response(
                    ProductSerializer(product).data, status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # If no photos are uploaded, just update the product details
        serializer = ProductUpdateSerializer(
            product, data=request.data, partial=partial
        )
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.prefetch_related(
            Prefetch("photos", queryset=Photo.objects.all(), to_attr="filtered_photos")
        )


class ProductBySellerListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Product.objects.filter(user_id=user_id).prefetch_related(
            Prefetch("photos", queryset=Photo.objects.all(), to_attr="filtered_photos")
        )


class ProductByStatusListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        status = self.kwargs["status"]
        return Product.objects.filter(status__iexact=status).prefetch_related(
            Prefetch(
                "photos",
                queryset=Photo.objects.filter(status__in=["Normal", "Bokeh"]),
                to_attr="filtered_photos",
            )
        )


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.prefetch_related("photos").all()
    serializer_class = ProductSerializer
    lookup_field = "code"


class ProductDeleteView(DestroyAPIView):
    queryset = Product.objects.prefetch_related("photos").all()
    serializer_class = ProductSerializer
    lookup_field = "code"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serialized_data = self.get_serializer(
            instance
        ).data  # Serialize data before deletion
        self.perform_destroy(instance)
        return Response(
            {"message": "Product successfully deleted.", "product": serialized_data},
            status=status.HTTP_200_OK,
        )

    def perform_destroy(self, instance):
        instance.delete()


class PhotoUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
