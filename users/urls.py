from django.urls import path

from .views import MeView, RegisterView, UserListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('users/', UserListView.as_view(), name='user-list'),
]
