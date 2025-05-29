from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password



User = get_user_model()


class UserDetailSerializer(BaseUserSerializer): 
    """ 
        Custom Serializer: 
        Uses for show details like username and password and extra fields like first and last name as well
    """
    class Meta(BaseUserSerializer.Meta):
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
        # Check if passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match.')
            
        # Custom password validations
        password = data['password']
        username = data['username']
        
        # Check if password contains username
        if username.lower() in password.lower():
            raise serializers.ValidationError({'password': ['Password cannot contain username.']})
            
        # Check password length
        if len(password) < 8:
            raise serializers.ValidationError({'password': ['Password must be at least 8 characters long.']})
            
        # Check if password is only numeric
        if password.isdigit():
            raise serializers.ValidationError({'password': ['Password cannot be entirely numeric.']})
            
        # Check if password is only alphabetic
        if password.isalpha():
            raise serializers.ValidationError({'password': ['Password must contain at least one number or special character.']})
        
        # Validate password strength using Django's password validators
        try:
            # This will validate against all validators in settings.AUTH_PASSWORD_VALIDATORS
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
            
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
