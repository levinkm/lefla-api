from distutils.util import change_root
from importlib.util import set_loader
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
    WebsocketConsumer,
    AsyncConsumer,
)
import json
import asyncio


class BookingNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print(self.scope["url_route"])
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat-%s" % self.room_name
        self.groups = [self.room_group_name]

        await self.send(
            text_data=json.dumps({"type": "tester_message", "tester": "sav4ner"}),
        )

    async def tester_message(self, event):
        tester = event["tester"]

        await self.send(text_data=json.dumps({"tester": tester}))

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


class ChatConsumer(AsyncWebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
