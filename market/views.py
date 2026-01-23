from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .permissions import IsAdmin, IsAdminHard, IsOwnerProduct, IsOwnerShop, IsSeller, IsSellerHard
from .models import (Category, Shop, Product, CommentProduct, ImageProduct,
                     ReviewProduct, ReviewShop, HistorySearch, Cart, Order)
from .serializer import (CategorySerializer, ShopSerializer, ProductSerializer,
                         ProductDetailSerializer, CartSerializer, OrderSerializer,
                         HistorySearchSerializer, ReviewProductSerializer, ReviewShopSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdmin | IsSeller]


