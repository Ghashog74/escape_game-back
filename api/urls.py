from django.urls import path
from .views import get_user, CustomTokenObtainPairView, CustomTokenRefreshView, logout, is_authenticated, register, create_game, get_game_history, update_user

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('get_user/', get_user),
    path('logout/', logout),
    path('authenticated/', is_authenticated),
    path('register/', register),
    path('create_game/', create_game),
    path('get_game_history/', get_game_history),
    path('update_user/', update_user)
]