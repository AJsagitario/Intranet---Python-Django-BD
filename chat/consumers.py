from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Channel, Message, ChannelMember
import json


User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close(); return

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.user_id = self.scope["user"].id

        # DM o Canal
        if self.room_name.startswith("dm-"):
            other_id = int(self.room_name.split("-", 1)[1])
            ok = await self._check_dm_allowed(other_id)
            if not ok:
                await self.close(); return
            # grupo DM (ordenado para que ambos usen el mismo)
            a, b = sorted([self.user_id, other_id])
            self.group_name = f"dm_{a}_{b}"
        else:
            self.group_name = f"chat_{self.room_name}"
            # Debe ser miembro del canal
            is_member = await self._user_in_channel(self.user_id, self.room_name)
            if not is_member:
                await self.close(); return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        payload = json.loads(text_data or "{}")
        body = (payload.get("body") or "").strip()
        if not body: return

        msg = await self._save_message(self.user_id, self.room_name, body)
        await self.channel_layer.group_send(self.group_name, {"type": "chat.message", "data": msg})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    # ----- helpers DB -----
    @database_sync_to_async
    def _user_in_channel(self, user_id, room_name):
        try:
            ch = Channel.objects.get(name=room_name)
            return ChannelMember.objects.filter(channel=ch, user_id=user_id).exists()
        except Channel.DoesNotExist:
            return False
        
    @database_sync_to_async
    def _check_dm_allowed(self, other_id):
        # En esta versión, todo usuario logueado puede DM a cualquier otro existente
        return User.objects.filter(id=other_id, is_active=True).exists()

    @database_sync_to_async
    def _save_message(self, user_id, room_name, body):
        u = User.objects.get(id=user_id)
        if room_name.startswith("dm-"):
            other_id = int(room_name.split("-", 1)[1])
            other = User.objects.get(id=other_id)
            m = Message.objects.create(channel=None, sender=u, receiver=other, body=body)
        else:
            ch = Channel.objects.get(name=room_name)
            m = Message.objects.create(channel=ch, sender=u, body=body)
        return {"user": u.get_username(), "body": m.body, "ts": m.created_at.isoformat(timespec="seconds")}
