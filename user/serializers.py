from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from rest_framework import serializers

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, validators = [validate_password])

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name"]

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists")

        return email

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
