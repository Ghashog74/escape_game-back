from itertools import count
from logging import NullHandler
from modulefinder import ReplacePackage

from django.shortcuts import render
from django.contrib.auth import get_user_model
from .serializer import UserSerializer, UserRegistrationSerializer, GameSerializer, GameDataSerializer, EnigmeSerializer
User = get_user_model()
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Game, Enigmes
from django.db.models import Q

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            token = response.data

            access_token = token['access']
            refresh_token = token['refresh']

            res = Response()

            res.data = {'success': True}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )
            res.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )

            return res
        except:
            res = Response({'success': False})
            return res

class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens['access']

            res = Response()

            res.data = {'refreshed': True}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                path='/',
            )

            return res
        except:
            return Response({'refreshed': False})

@api_view(['POST'])
def logout(request):
    try:
        res = Response()
        res.data = {'success': True}
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')
        return res
    except:
        return Response({'success': False})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    return Response({'authenticated': True})

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = User.objects.get(id=request.user.id)
    serializer = UserSerializer(user)

    return Response({'user': serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_game(request):
    game = Game.objects.filter(Q(game_code=request.data["game_code"]))
    if game.count():
        return(Response({"success": False,"error": "game already exist"}))
    data = request.data
    data['time_spend'] = 0
    data['hint_left'] = 3
    data['progress'] = 0
    data['status'] = "progress"
    data['p1'] = request.user.id
    print(data)
    serializer = GameSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"success": True})
    return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_history(request):
    user = request.user
    games = Game.objects.filter((Q(p1=user) | Q(p2=user)) & ~Q(p2=None))
    serializer = GameDataSerializer(games, many=True, context={'request': request})
    return Response({'games': serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_game(request):
    user = request.user
    activeGame = Game.objects.filter((Q(p1=user) | Q(p2=user)) & Q(status="progress"))
    if activeGame.count():
        serializer = GameDataSerializer(activeGame[0], context={'request': request})
        if serializer.data["p2_username"]:
            p2name = serializer.data["p2_username"]
        else:
            p2name = "none"
        return Response({
            "active": True,
            "game_code": activeGame[0].game_code,
            "p2": p2name
        })
    return Response({
        "active": False
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def game_exist(request):
    if(request.data["game_code"] == '' or (str(request.data["game_code"]).__len__()) != 6):
        return Response({"exist": False})
    activeGame = Game.objects.filter(Q(game_code=request.data["game_code"]) & Q(status="progress") & Q(p2=None))
    if activeGame.count():
        return Response({"exist": True})
    else:
        return Response({"exist": False})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_game(request):
    user = User.objects.get(id=request.user.id)
    game = Game.objects.get(game_code=request.data['game_code'])
    data = {'p2': user.id}
    serializer = GameSerializer(game, data=data, partial=True)
    if(serializer.is_valid()):
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_game(request):
    game = Game.objects.get(game_code=request.data['game_code'])
    game.delete()
    return Response({
        'success': 'game deleted successfully'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_game(request):
    game = Game.objects.get(game_code=request.data['game_code'])
    serializer = GameSerializer(game, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_game_info(request):
    game = Game.objects.get(game_code=request.data['game_code'])
    serializer = GameSerializer(game, context={'request': request})

    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_enigme(request):
    try:
        enigme = Enigmes.objects.get(progress=request.data['progress'])
        serializer = EnigmeSerializer(enigme)
        return Response({
            'enigme': serializer.data
        })
    except:
        return Response({
            'error': 'aucune énigme trouver'
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_enigme(request):
    try:
        enigme = Enigmes.objects.get(progress=request.data['progress'])
        serializer = EnigmeSerializer(enigme)
        if serializer.data['solution'].lower() == request.data['reponse'].lower():
            return Response({'correct': True})
        return Response({'correct': False})
    except:
        return Response({
            'error': 'aucune énigme trouver'
        })



