from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model exposing id, email, and username fields.
    """
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
        ]


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password confirmation.

    Fields:
        - fullname (write_only): Full name input as a single string.
        - email: User email, must be unique.
        - password (write_only): User password.
        - repeated_password (write_only): Confirmation of password, must match password.

    Validations:
        - Checks if email is already registered.
        - Checks if password and repeated_password match.

    Save method:
        - Splits fullname into first_name and last_name.
        - Sets username by replacing spaces with '//'.
        - Creates and saves a new User instance with hashed password.
    """
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "repeated_password": {"write_only": True},
        }

    def removeSpaces(self, value):
        return value.replace(" ", "//")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def save(self, **kwargs):
        pw = self.validated_data["password"]
        repeated_password = self.validated_data["repeated_password"]
        if pw != repeated_password:
            raise serializers.ValidationError(
                {"error": "Passwords do not match"})

        fullname = self.validated_data.get("fullname", "")
        first_name, *last_parts = fullname.strip().split(" ")
        last_name = " ".join(last_parts) if last_parts else ""
        username = self.removeSpaces(fullname)

        account = User(
            username=self.validated_data["fullname"],
            first_name=first_name,
            last_name=last_name,
            email=self.validated_data["email"],
        )
        account.set_password(pw)
        account.save()
        return account
