from rest_framework import routers
from gamemode.viewsets import RouletteViewSet
from account.viewsets import UserViewSet


from gamemode.viewsets import UserBalanceViewSet, WheelFortuneViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"roulette", RouletteViewSet)
router.register(r"user_balance", UserBalanceViewSet)
router.register(r"wheel_fortune", WheelFortuneViewSet)