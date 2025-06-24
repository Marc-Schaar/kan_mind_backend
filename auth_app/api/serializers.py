from rest_framework import serializers
from auth_app.models import UserProfile
from django.contrib.auth.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user']


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True},
                        'repeated_password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self, **kwargs):
        pw = self.validated_data['password']
        repeated_password = self.validated_data['repeated_password']
        if pw != repeated_password:
            raise serializers.ValidationError(
                {'error': "Passwords do not match"})

        account = User(
            username=self.validated_data['username'],
            email=self.validated_data['email']
        )
        account.set_password(pw)
        account.save()
        return account
