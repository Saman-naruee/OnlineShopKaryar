from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import serializers
from djoser import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer as BaseUserCreateSerializer

User = get_user_model()

# class UserCreateSerializer(BaseUserCreateSerializer):

#     class Meta(BaseUserCreateSerializer.Meta):
#         fields = [
#             'id', 'username', 'password', 'email', 'first_name', 'last_name'
#         ]


class UserDetailSerializer(UserSerializer): # we have to modify it in settings.DJOSER settings.
    """ 
        Custom Serializer: 
        Uses for show details like username and password and extra fields like first and last name as well
    """
    class Meta(UserSerializer.Meta):
        fields = [
            'id', 'username', 'password', 'email', 'first_name', 'last_name'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'first_name', 'last_name']

        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True},
            'password2': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError('Invalid email address.')

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match.')
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['email']  # Email cannot be changed once set
