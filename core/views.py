from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer
from django.views.generic import TemplateView


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Register a new user with email and username validation
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update user profile.
    Email cannot be changed once set.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Prevent email changes
        if 'email' in request.data and request.data['email'] != instance.email:
            return Response(
                {"detail": "Email cannot be changed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_update(serializer)
        return Response(serializer.data)


class HomeView(TemplateView):
    template_name = 'home.html'
