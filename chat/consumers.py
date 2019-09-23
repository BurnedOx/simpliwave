# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import Message
from employee.models import ProjectManagement
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def create_message(self, data):
        Message.objects.create(
            sender=data['sender'],
            room=data['room'],
            message=data['message']
        )
        message = Message.objects.filter(room=data['room'], sender=data['sender'], message=data['message']).latest('id')
        group = ProjectManagement.objects.get(name=data['room'])
        group.messages.add(message)

    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        messages = ProjectManagement.objects.get(name=self.room_name).messages.all()
        for message in messages:
            await self.send(text_data=json.dumps({
                'message': message.message,
                'sender': message.sender.username
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )
        data = {
            'sender': User.objects.get(username=sender),
            'room': self.room_name,
            'message': message
        }

        await self.create_message(data=data)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
