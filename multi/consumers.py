import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            'success': True,
            'subject': 'request_code',
            'message': 'successfully connected please send a room code'
        }))

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data['subject'] == 'create_game':
            self.room_group_name = data['game_code']
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.send(text_data=json.dumps({
                'success': True,
                'subject': 'success',
                'message': f"You created the room n° {self.room_group_name}"
            }))
        elif data['subject'] == 'join_game':
            self.room_group_name = data['game_code']
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'joined_message',
                    'message': 'A new player as joined the room'
                }
            )

    def joined_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'success': True,
            'subject': 'joined',
            'message': message
        }))