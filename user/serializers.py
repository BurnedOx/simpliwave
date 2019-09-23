from rest_framework import serializers
from rest_framework import exceptions
from django.contrib.auth import authenticate


class AuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username', '')
        password = data.get('password', '')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise exceptions.ValidationError('User is deactivated')
            else:
                raise exceptions.ValidationError('Unable to login with given credentials')
        else:
            raise exceptions.ValidationError('Must provide username and password both')

        return data
