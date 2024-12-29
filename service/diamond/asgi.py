"""
ASGI config for diamond project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diamond.settings")

django_asgi_app = get_asgi_application()

from api.middleware import SimpleJWTAuthTokenMiddleware, QueryStringSimpleJWTAuthTokenMiddleware
from gamemode.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": SimpleJWTAuthTokenMiddleware(QueryStringSimpleJWTAuthTokenMiddleware(URLRouter(websocket_urlpatterns))),
})

