from rest_framework import serializers
from apps.cpf_search.models import Cpf
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CpfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cpf
        fields = ["cpf", "nome", "nasc", "sexo"]


class CustomRegisterSerializer(RegisterSerializer):
    def validate_password(self, password):
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return password
