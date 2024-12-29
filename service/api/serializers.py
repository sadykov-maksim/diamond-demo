from typing import Dict, Any
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainSerializer, \
    TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from account.models import Account

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'username', 'email', 'image', 'signature',  'banner',  'privacy_settings', 'friends_visibility', 'inventory_visibility']




class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken('No valid token found in cookie \'refresh_token\'')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        if self.user:
            user_data = {
                "id": self.user.id,
                "username": self.user.username,
                "email": self.user.email,
            }

            if hasattr(self.user, 'image') and self.user.image:
                user_data['image'] = self.user.image.url

            data['user'] = user_data
        return data