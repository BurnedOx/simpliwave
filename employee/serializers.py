from rest_framework import serializers
from rest_framework import exceptions
from .models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = '__all__'


class EmployeeIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeId
        fields = ['id', 'user', 'employeeId', 'name', 'email', 'about', 'contact', 'image', 'skills', 'projectHistory', 'last_seen', 'online']


class MilestoneSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Milestone
        fields = '__all__'


class ProjectManagementSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = ProjectManagement
        fields = '__all__'


class FileManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileManagement
        fields = '__all__'


class ResultSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = Result
        fields = ['id', 'name', 'points', 'role', 'creditPercentage']

    def validate(self, data):
        credit = data.get('creditPercentage', '')
        if int(credit) > 100:
            raise exceptions.ValidationError('percentage should be less than or equal to 100')
        return data


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
