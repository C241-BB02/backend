from django.shortcuts import render
from rest_framework import generics
from .serializers import User, UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
