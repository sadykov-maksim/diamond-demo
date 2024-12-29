from rest_framework import serializers, viewsets
from .models import Account

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'