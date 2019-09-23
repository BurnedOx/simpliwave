from rest_framework import serializers
from rest_framework import exceptions
import re
from .models import *


def validate_password(password):
    if len(password) < 8:
        raise exceptions.ValidationError('Password should be atleast 8 characters long')
    elif ' ' in password:
        raise exceptions.ValidationError('Password should not contain any space')
    elif not bool(re.match('^(?=.*[0-9]$)(?=.*[a-zA-Z])', password)):
        raise exceptions.ValidationError('Password should contain atleast one alphabet and numeric')
    return password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']

    def validate(self, data):
        email = data.get('email', '')
        password = data.get('password', '')
        if email and password:
            data['password'] = validate_password(password)
        else:
            raise exceptions.ValidationError('Must provide both email and password')
        return data


class PasswordUpdateSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)
    confirmPassword = serializers.CharField(write_only=True)

    class Meta:
        fields = ['oldPassword', 'newPassword', 'confirmPassword']

    def validate(self, attrs):
        old_password = attrs.get('oldPassword', '')
        new_password = attrs.get('newPassword', '')
        confirm_password = attrs.get('confirmPassword', '')
        if old_password and new_password and confirm_password:
            attrs['newPassword'] = validate_password(new_password)
            if confirm_password != new_password:
                raise exceptions.ValidationError("Confirm Password didn't match")
        else:
            raise exceptions.ValidationError('Must provide all the fields')
        return attrs


class EmailUpdateSerializer(serializers.Serializer):
    email = serializers.CharField()

    class Meta:
        fields = 'email'


class NameUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        fields = ['first_name', 'last_name']


class NameApproveSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()

    class Meta:
        model = NameApprove
        fields = ['id', 'student', 'old_name', 'first_name', 'last_name', 'status']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'name', 'email', 'about', 'contact', 'image', 'skills', 'projectHistory', 'credits', 'last_seen', 'online', 'status']


class VerifySerializer(serializers.Serializer):
    code = serializers.CharField()

    class Meta:
        fields = 'code'


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):
    countOfProjects = serializers.ReadOnlyField()
    label = serializers.ReadOnlyField()

    class Meta:
        model = Experience
        fields = '__all__'


class ProjectApplySerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField()

    class Meta:
        model = ProjectApply
        fields = ['id', 'student', 'project', 'status']


class ProjectApplyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectApply
        fields = ['status']


class InternshipApplySerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipApply
        fields = '__all__'


class ProjectComposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCompose
        fields = '__all__'


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = '__all__'


class CodeSharingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSharing
        fields = '__all__'
