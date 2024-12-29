import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from requests import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.serializers import CookieTokenRefreshSerializer, MyTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import logging
logger = logging.getLogger(__name__)
# Create your views here.


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    def finalize_response(self, request, response, *args, **kwargs):

        if 'user' in response.data:
            user = response.data['user']
            if user:
                # Directly access user attributes
                response.data['user'] = {
                    "id": user['id'],
                    "username": user['username'],
                    "image": user.get('image', None),
                    "email": user['email'],

                }
        response = super().finalize_response(request, response, *args, **kwargs)

        if response.data.get('refresh'):
            cookie_max_age = 3600 * 24 * 14
            response.set_cookie('refresh_token', response.data['refresh'],  max_age=cookie_max_age, httponly=True,
                                samesite='Lax', secure=True)
            del response.data['refresh']
        return response


class CookieTokenRefreshView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            cookie_max_age = 3600 * 24 * 14
            response.set_cookie('refresh_token', response.data['refresh'], max_age=cookie_max_age,  httponly=True,
                                samesite='Lax', secure=True)
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)
    serializer_class = CookieTokenRefreshSerializer

