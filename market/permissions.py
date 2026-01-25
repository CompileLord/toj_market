from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'AD' or request.user.is_staff)
        )

class IsAdminHard(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'AD' or request.user.is_staff)
        )
    

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'SL'
        )

class IsSellerHard(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'SL'
        )

class IsOwnerShop(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user

class IsOwnerImageProduct(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'SL'
        )
    
    def has_object_permission(self, request, view, obj):
        return obj.product.shop.seller == request.user


class IsOwnerProduct(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.shop.seller == request.user