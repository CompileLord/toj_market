from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count, Q, DecimalField, Prefetch
from django.db.models.functions import Coalesce

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


class ShopViewSet(viewsets.ModelViewSet):
    serializer_class = ShopSerializer
    permission_classes = [IsAdmin | IsOwnerShop]
    queryset = Shop.objects.all()
    
    def get_queryset(self):
        return Shop.objects.annotate(
            avg_crowns = Coalesce(
                Avg('products__product_crowns__crowns'),
                0,
                output_field=DecimalField()
            ),
            total_products = Count('products', distinct=True),
            total_orders = Count('products__orders', distinct=True)
        ).select_related('seller')
    

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin | IsOwnerProduct]
    queryset = Product.objects.all()
    
    def get_queryset(self):
        queryset = Product.objects.annotate(
            avg_crowns=Coalesce(
                Avg('product_crowns__crowns'),
                0.0,
                output_field=DecimalField()
            )
        ).select_related('shop', 'category')
        if self.action == 'list':
            return queryset.prefetch_related(
                Prefetch(
                    'images',
                    queryset=ImageProduct.objects.filter(is_main_image=True), 
                )
            )        
        if self.action == 'retrieve':
            return queryset.prefetch_related('images', 'comments__user')        
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    



        


