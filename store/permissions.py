from typing import override
from rest_framework.permissions import BasePermission
from rest_framework import permissions

from store.models import Cart, CartItem

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class ViewCustomerHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')   # app name + . + permission name


class NotificationsPermission(permissions.BasePermission):
    """
    Custom permission for Notifications:
    - Only admin can create, update and delete notifications.
    - Users can only read their own notifications.
    """
    def has_permission(self, request, view):
        # Allow authenticated users to list/retreive
        if request.method in permissions.SAFE_METHODS: # SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
            return bool(request.user and request.user.is_authenticated)
    
        # Only admin can create notifications
        return bool(request.user and request.user.is_staff and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Check if the user is trying to view their own notification
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user and request.user.is_authenticated
        
        # Only admin can update and delete notifications
        return bool(request.user and request.user.is_staff and request.user.is_authenticated)

class IsCartOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a cart to view, edit or delete it.
    """
    def has_permission(self, request, view, obj=None):
        cart_id = view.kwargs.get('cart_pk')
        try:
            cart = Cart.objects.get(pk=cart_id)
            return cart.user == request.user
        except Cart.DoesNotExist:
            return False
    

class IsCartItemOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a cart item to view, edit or delete it.
    """
    def has_permission(self, request, view, obj=None):
        cart_item_id = view.kwargs.get('pk')
        try:
            cart_item = CartItem.objects.get(pk=cart_item_id)
            return cart_item.cart.user == request.user
        except CartItem.DoesNotExist:
            return False
