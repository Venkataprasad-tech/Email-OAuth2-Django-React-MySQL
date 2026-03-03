from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from rest_framework.authtoken.models import Token

import requests
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer

from .serializers import SignUpSerializer, SignInSerializer
from .models import User
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import AllowAny

User = get_user_model()



@ensure_csrf_cookie
@api_view(["GET"])
@permission_classes([AllowAny])
def get_csrf(request):
    return JsonResponse({"detail": "CSRF cookie set"})


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user

    return Response({
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "photo_url": getattr(user, "photo_url", None),  # for Google
        "auth_provider": getattr(user, "auth_provider", "email")
    })



@csrf_exempt
@api_view(['POST'])
def signup(request):
    data = request.data

    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')

    if not full_name or not email or not password:
        return Response(
            {"error": "All fields are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=full_name
    )

    return Response(
        {"message": "Account created successfully"},
        status=status.HTTP_201_CREATED
    )
    
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(request, username=email, password=password)

    if user:
        login(request, user)  # ← THIS CREATES SESSION
        return Response({
            "message": "Login successful",
            "email": user.email,
            "first_name": user.first_name,
            "auth_provider": "email"
        })

    return Response({"error": "Invalid credentials"}, status=400)



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    access_token = request.data.get('access_token')

    if not access_token:
        return Response(
            {"error": "Access token required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    
    google_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    google_response = requests.get(google_url, headers=headers)

    if google_response.status_code != 200:
        return Response(
            {"error": "Invalid Google token"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user_info = google_response.json()

    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    if not email:
        return Response(
            {"error": "Google account email not available"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 🔹 Create or get user
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": email,
            "first_name": name or "",
        }
    )

    return Response(
        {
            "message": "Google login successful",
            "email": user.email,
            "name": user.first_name,
            "new_user": created,
            "user": {
                "first_name": user.first_name,
                "email": user.email,
                "auth_provider": "google",
                "avatar": picture
            }
        },
        status=status.HTTP_200_OK
    )
