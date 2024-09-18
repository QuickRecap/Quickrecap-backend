from rest_framework import generics, status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate

from .models import *
from .serializers import *

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'nombres', 'apellidos', 'celular', 'genero', 'fecha_nacimiento']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            nombres=validated_data['nombres'],
            apellidos=validated_data['apellidos'],
            celular=validated_data.get('celular', None),
            genero=validated_data.get('genero', None),
            fecha_nacimiento=validated_data.get('fecha_nacimiento', None),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    return user
                else:
                    raise serializers.ValidationError("Cuenta inactiva.")
            else:
                raise serializers.ValidationError("Credenciales incorrectas.")
        else:
            raise serializers.ValidationError("Debes proporcionar ambos campos.")

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
