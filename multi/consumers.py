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

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'close_message'
            }
        )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        subject = data['subject']
        if subject == 'create_game':
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




        elif subject == 'join_game':
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

        elif subject == 'leave_game':
            code = self.room_group_name
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
            self.send(text_data=json.dumps({
                'success': True,
                'subject': 'leave_game',
                'message': f"You have left the room {self.room_group_name}"
            }))
            async_to_sync(self.channel_layer.group_send)(
                code,
                {
                    'type': 'close_message',
                }
            )

        elif subject == 'check_game':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'check_message',
                    'sender_channel_name': self.channel_name
                }
            )
        elif subject == 'game_checked':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'checked_message',
                    'sender_channel_name': self.channel_name
                }
            )
        elif subject == 'player_data':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'username_message',
                    'sender_channel_name': self.channel_name,
                    'username': data['username']
                }
            )
        elif subject == 'close':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'close_message'
                }
            )
        elif subject == 'continue_game':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'continue_message',
                    'sender_channel_name': self.channel_name
                }
            )
        elif subject == 'update_response':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_response_message',
                    'sender_channel_name': self.channel_name,
                    'response': data['response']
                }
            )
        elif subject == 'update_progress':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'update_progress_message',
                    'sender_channel_name': self.channel_name,
                    'progress': data['progress']
                }
            )

    def update_progress_message(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'success': True,
                'subject': 'update_progress',
                'progress': event['progress']
            }))

    def update_response_message(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'success': True,
                'subject': 'update_response',
                'response': event['response']
            }))

    def continue_message(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'success': True,
                'subject': 'continue_game'
            }))

    def close_message(self, event):
        self.send(text_data=json.dumps({
            'success': True,
            'subject': 'pause'
        }))

    def username_message(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'success': True,
                'subject': 'p2_data',
                'username': event['username']
            }))

    def checked_message(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'success': True,
                'subject': 'game_checked',
            }))

    def check_message(self, event):
        if self.channel_name != event['sender_channel_name']:
            self.send(text_data=json.dumps({
                'success': True,
                'subject': 'check_game',
            }))


    def joined_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'success': True,
            'subject': 'joined',
            'message': message
        }))