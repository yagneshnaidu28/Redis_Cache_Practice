from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.create_user),
    path('users/all/', views.get_users),
    path('users/<int:user_id>/', views.get_user),
    path('users/<int:user_id>/update/', views.update_user),
    path('users/<int:user_id>/delete/', views.delete_user),
]