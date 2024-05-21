
from django.urls import path

from sms.consumer import ChatConsumer

websocket_urlpatterns = [
    path(r"sms/", ChatConsumer.as_asgi())
]
