from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema

from django.db.models import Avg, Count, Q, DecimalField, Prefetch
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

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
    
    def list(self, request, *args, **kwargs):
        cache_key = 'shop_list'
        data = cache.get(cache_key)
        if not data:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            data = serializer.data
            cache.set(cache_key, data, 60)
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cache_key = f'shop_detail_{pk}'
        data = cache.get(cache_key)

        if not data:
            shop = self.get_object()
            data = ShopSerializer(shop).data
            cache.set(cache_key, data, 60)
        
        return Response(data)

    def perform_create(self, serializer):
        serializer.save()
        cache.clear()
    
    def perform_update(self, serializer):
        serializer.save()
        cache.clear()
    
    def perform_destroy(self, instance):
        instance.delete()
        cache.clear()


    

class ProductViewSet(viewsets.ViewSet):
    
    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsOwnerProduct | IsAdmin]
        return [permissions() for permission in permission_classes]

    def list(self, request):
        queryset = Product.objects.all().select_related('shop', 'category')
        cache_key = 'list_shop'
        data = cache.get(cache_key)
        if not data:
            serializer = ProductSerializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60)
        return Response(data)
    
    def retrieve(self, request, pk=None):
        queryset = Product.objects.all()
        product = get_object_or_404(queryset, pk=pk)
        cache_key = f'product_detail_{pk}'
        data = cache.get(cache_key)
        if not data:
            serializer = ProductDetailSerializer(product)
            data = serializer.data
            cache.set(cache_key, data, 60)

        if request.user.is_authenticated:
            review_serializer = ReviewProductSerializer(
                data={'product': product.id},
                context={'request': request}
            )
            if review_serializer.is_valid():
                review_serializer.save(product=product)

        return Response(data)
    
    def performe_create(self, serializer):
        serializer.save()
        cache.clear()
    
    def performe_update(self, serializer):
        serializer.save()
        cache.clear()
    
    def performe_destroy(self, instance):
        instance.delete()
        cache.clear()

    



        


