from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
from rest_framework_jwt.utils import jwt_decode_handler
from sms.models import SMS
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        try:
            query_string = self.scope['query_string'].decode()
            token = query_string.split('&')[0].split('=')[1]
            # print(query_string, 'query')

            # Decode and validate the token (JWT example)
            payload = jwt_decode_handler(token)
            user_id = payload['user_id']
            user = await self.get_user(user_id)
            # print(user)

            if user:
                # Authentication successful
                self.user = user
                await self.channel_layer.group_add('chatroom', self.channel_name)
                await self.accept()
            else:
                await self.close(code=4003)  # Unauthorized
        except Exception as e:
            await self.close(code=4003)  # Invalid token

    # ... (rest of your consumer logic)

    async def disconnect(self, code):
        await self.channel_layer.group_discard('chatroom', self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        message = text_data_json['message']
        username = self.user.username
        # print(message)

        mod = await self.delete_data(message)

        # Send message to chatroom
        await self.channel_layer.group_send(
            'chatroom',
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    # Handle chat messages
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        data = await self.get_data()

        await self.send(text_data=json.dumps({
            'message': data,
            'username': username,
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_data(self):
        try:
            return list(SMS.objects.all().values())
        except Exception as e:
            return None

    @database_sync_to_async
    def delete_data(self, phone_number):
        try:
            mod = SMS.objects.filter(phone_number=phone_number)
            if mod.exists():
                mod.delete()
        except SMS.DoesNotExist:
            return None
