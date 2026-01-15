from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        """
        Validates:
        - password matches repeated_password
        - email is unique
        - password passes Django password validators
        """
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({"repeated_password": "Passwords do not match."})

        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")

        user = User.objects.create_user(password=password, **validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        return user, token


class LoginSerializer(serializers.Serializer):
    """Validates credentials (email + password)."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError({"detail": "Invalid credentials."})

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return user, token
