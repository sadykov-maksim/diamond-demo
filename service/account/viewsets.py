from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import Account
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = UserSerializer