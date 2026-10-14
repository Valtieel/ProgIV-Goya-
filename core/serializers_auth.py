from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    # write_only: la contraseña se recibe, pero nunca se devuelve en una respuesta.
    # validate_password aplica las reglas de Django (largo mínimo, no muy común, etc.)
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_email(self, value):
        # El modelo User de Django no obliga a que el email sea único, lo controlamos acá.
        # email__iexact compara sin distinguir mayúsculas de minúsculas.
        if value and User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese email.")
        return value

    def create(self, validated_data):
        # create_user hashea la contraseña antes de guardarla.
        # El create por defecto la guardaría en texto plano, por eso lo reemplazamos.
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )