from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from drf_yasg.utils import swagger_auto_schema

from django.db.models import Avg, Count, DecimalField
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.core.cache import cache

from .permissions import IsAdmin, IsOwnerProduct, IsOwnerShop
from .models import (Category, Shop, Product, ReviewProduct)
from .serializer import (CategorySerializer, ShopSerializer, ProductSerializer,
                         ProductDetailSerializer, ReviewProductSerializer)




class ShopListCreateView(generics.ListCreateAPIView):
    serializer_class = ShopSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdmin | IsOwnerShop]
    
    def get_queryset(self):
        return Shop.objects.annotate(
            avg_crowns=Coalesce(
                Avg('products__product_crowns__crowns'),
                0,
                output_field=DecimalField()
            ),
            total_products=Count('products', distinct=True),
            total_orders=Count('products__orders', distinct=True)
        ).select_related('seller')
    
    @swagger_auto_schema(tags=['Shop'])
    def get(self, request, *args, **kwargs):
        cache_key = 'shop_list'
        data = cache.get(cache_key)
        if not data:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            data = serializer.data
            cache.set(cache_key, data, 60)
        return Response(data)
    
    @swagger_auto_schema(
        tags=['Shop'],
        consumes=['multipart/form-data'],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        cache.clear()
        return response
    

# ---- Category ----  

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(tags=['Category'], consumes=['multipart/form-data']) 
    def get(self, request, *args, **kwargs):
        cache_key = 'category_list'
        data = cache.get(cache_key)
        if not data:
            queryset = Category.objects.annotate(
                total_products=Count('category_products', distinct=True),
            )
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60)
        return Response(data)

class CategoryDetailView(generics.RetrieveAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdmin]
    @swagger_auto_schema(tags=['Category'], consumes=['multipart/form-data'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    @swagger_auto_schema(tags=['Category'], consumes=['multipart/form-data']) 
    def post(self, request, *args, **kwargs):
        cache.clear()
        return super().post(request, *args, **kwargs)
  
    
class CategoryPutView(generics.UpdateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdmin]
    http_method_names = ['put']
    @swagger_auto_schema(tags=['Category'], consumes=['multipart/form-data']) 
    def put(self, request, *args, **kwargs):
        cache.clear()
        return super().put(request, *args, **kwargs)  
    

class CategoryDestroyView(generics.DestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdmin]
    @swagger_auto_schema(tags=['Category'], consumes=['multipart/form-data']) 
    def delete(self, request, *args, **kwargs):
        cache.clear()
        return super().delete(request, *args, **kwargs)


# ------- Shop -----

class ShopListView(generics.ListAPIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(tags=['Shop'], consumes=['multipart/form-data'])  
    def get(self, request, *args, **kwargs):
        cahce_key = 'shop_list'
        data = cache.get(cahce_key)
        if not data:
            queryset = Shop.objects.annotate(
                avg_crowns=Coalesce(
                    Avg('products__product_crowns__crowns'),
                    0,
                    output_field=DecimalField()
            )
            ).select_related('seller')
            serializer = self.serializer_class(queryset, many=True)
            data = serializer.data
            cache.set(cahce_key, data, 60)
        return Response(data)
    
class ShopDetailView(generics.RetrieveAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    @swagger_auto_schema(tags=['Shop'], consumes=['multipart/form-data'])  
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        shop = get_object_or_404(Shop, pk=pk)
        cache_key = f'shop_detail_{pk}'
        data = cache.get(cache_key)
        if not data:
            serializer = self.get_serializer(shop)
            data = serializer.data
            cache.set(cache_key, data, 60)
        
        return Response(serializer.data)

class ShopCreateView(generics.CreateAPIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAdmin | permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    @swagger_auto_schema(tags=['Shop'], consumes=['multipart/form-data'])  
    def post(self, request, *args, **kwargs):
        cache.clear()
        return super().post(request, *args, **kwargs)

class ShopPutView(generics.UpdateAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    permission_classes = [IsAdmin | IsOwnerShop]
    http_method_names = ['put']
    @swagger_auto_schema(tags=['Shop'], consumes=['multipart/form-data'])  
    def put(self, request, *args, **kwargs):
        cache.clear()
        return super().put(request, *args, **kwargs)

class ShopDestroyView(generics.DestroyAPIView):
    serializer_class = ShopSerializer
    queryset = Shop.objects.all()
    permission_classes = [IsAdmin | IsOwnerShop]
    @swagger_auto_schema(tags=['Shop'], consumes=['multipart/form-data'])  
    def delete(self, request, *args, **kwargs):
        cache.clear()
        return super().delete(request, *args, **kwargs)


# ---- Product ----

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def get(self, request, *args, **kwargs):
        cache_key = 'product_list'
        data = cache.get(cache_key)
        if not data:
            queryset = Product.objects.annotate(
                avg_crowns=Coalesce(
                    Avg('product_crowns__crowns'),
                    0,
                    output_field=DecimalField()
                )
            ).select_related('shop')
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            cache.set(cache_key, data, 60)
        return Response(data)

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        product = get_object_or_404(Product, pk=pk)
        cache_key = f'product_detail_{pk}'
        data = cache.get(cache_key)
        if not data:
            serializer = self.get_serializer(product)
            data = serializer.data
            cache.set(cache_key, data, 60)
        return Response(data)

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin | IsOwnerShop]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def post(self, request, *args, **kwargs):
        cache.clear()
        return super().post(request, *args, **kwargs)

class ProductPutView(generics.UpdateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAdmin | IsOwnerProduct]
    http_method_names = ['put']
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def put(self, request, *args, **kwargs):
        cache.clear()
        return super().put(request, *args, **kwargs)

class ProductDestroyView(generics.DestroyAPIView):
    serializer_class = ProductSerializer
    queryset =Product.objects.all()
    permission_classes = [IsAdmin | IsOwnerProduct]
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def delete(self, request, *args, **kwargs):
        cache.clear()
        return super().delete(request, *args, **kwargs)

class ProductImageView(generics.ListAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]






    

    








    



        


