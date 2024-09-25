from djoser.serializers import UserSerializer, UserCreateSerializer as BaseUserCreateSerializer

class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        fields = [
            'id', 'username', 'password', 'email', 'first_name', 'last_name'
        ]


class UserDetailSerializer(UserSerializer): # we have to modify it in settings.DJOSER settings.
    """ 
        Custom Serializer: 
        Uses for show details like username and password and extra fields like first and last name as well
    """
    class Meta(UserSerializer.Meta):
        fields = [
            'id', 'username', 'password', 'email', 'first_name', 'last_name'
        ]
    