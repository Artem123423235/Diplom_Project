from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Профиль пользователя. Роль менять через API нельзя — только через админку."""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'full_name',
            'role', 'date_joined', 'last_login',
        )
        read_only_fields = ('id', 'role', 'date_joined', 'last_login')


class UserRegisterSerializer(serializers.ModelSerializer):
    """Регистрация. Пароль валидируется django-валидаторами."""

    password = serializers.CharField(
        write_only=True, validators=[validate_password], style={'input_type': 'password'}
    )
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password', 'password2')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password2': 'Пароли не совпадают.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
