from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

from .models import User
from .serializers import UserSerializer


# CREATE USER
@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        cache.delete("users_all")

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET ALL USERS
@api_view(['GET'])
def get_users(request):
    cached_users = cache.get("users_all")

    if cached_users is not None:
        return Response({
            "source": "Redis",
            "data": cached_users
        })

    users = User.objects.all()
    serializer = UserSerializer(users, many=True)

    cache.set("users_all", serializer.data, timeout=300)

    return Response({
        "source": "MySQL",
        "data": serializer.data
    })


# GET SINGLE USER
@api_view(['GET'])
def get_user(request, user_id):
    cache_key = f"user_{user_id}"

    cached_user = cache.get(cache_key)

    if cached_user is not None:
        return Response({
            "source": "Redis",
            "data": cached_user
        })

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserSerializer(user)

    cache.set(cache_key, serializer.data, timeout=300)

    return Response({
        "source": "MySQL",
        "data": serializer.data
    })


# UPDATE USER
@api_view(['PUT'])
def update_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserSerializer(user, data=request.data)

    if serializer.is_valid():
        serializer.save()

        cache.delete(f"user_{user_id}")
        cache.delete("users_all")

        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE USER
@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    user.delete()

    cache.delete(f"user_{user_id}")
    cache.delete("users_all")

    return Response({"message": "User deleted successfully"})