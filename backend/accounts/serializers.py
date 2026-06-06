"""Sérialiseurs pour l'app accounts."""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer en lecture pour l'utilisateur connecté."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = fields


class SignupSerializer(serializers.ModelSerializer):
    """Inscription d'un nouvel utilisateur. Mot de passe en écriture seule."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Au moins 8 caractères.",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]
        extra_kwargs = {
            "email":      {"required": True, "allow_blank": False},
            "first_name": {"required": False},
            "last_name":  {"required": False},
        }

    def validate_password(self, value: str) -> str:
        """Applique les AUTH_PASSWORD_VALIDATORS de Django (longueur, robustesse,
        similarité avec les autres champs, mots de passe trop communs…)."""
        try:
            django_validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Authentification : renvoie l'utilisateur si OK, lève ValidationError sinon."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs: dict) -> dict:
        user = authenticate(
            request=self.context.get("request"),
            username=attrs.get("username"),
            password=attrs.get("password"),
        )
        if user is None:
            raise serializers.ValidationError("Identifiants invalides.")
        if not user.is_active:
            raise serializers.ValidationError("Compte désactivé.")
        attrs["user"] = user
        return attrs
