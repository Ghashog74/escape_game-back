import locale

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Game, Enigmes
from datetime import datetime


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'created_at')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        #user.set_password(validated_data['password'])
        user.save()
        return user

class GameSerializer(serializers.ModelSerializer):
    p1_username = serializers.SerializerMethodField()
    p2_username = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ('start_date', 'session_start', 'time_spend', 'hint_left', 'progress', 'game_code', 'status', 'p1_username', 'p2_username', 'p1', 'p2')

    def get_p1_username(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        current_user = request.user
        if obj.p2 == current_user:
            return 'me'
        else:
            return obj.p2.username if obj.p2 else None

    def get_p2_username(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        current_user = request.user
        if obj.p1 == current_user:
            return 'me'
        else:
            return obj.p1.username if obj.p1 else None


class GameDataSerializer(serializers.ModelSerializer):
    p2_username = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ('start_date', 'time_spend', 'status', 'p2_username')

    def get_p2_username(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        current_user = request.user
        if obj.p1 == current_user:
            return obj.p2.username if obj.p2 else None
        else:
            return obj.p1.username if obj.p1 else None

    def get_start_date(self, obj):
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Linux/Mac
        except locale.Error:
            locale.setlocale(locale.LC_TIME, '')
        return obj.start_date.strftime('%-d %B %Y')

class EnigmeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enigmes
        fields = ('text_p1', 'text_p2', 'question', 'solution', 'hint', 'type', 'name', 'description', 'progress')