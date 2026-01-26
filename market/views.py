from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from drf_yasg.utils import swagger_auto_schema

from django.db.models import Avg, Count, DecimalField
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.core.cache import cache
from django.db import transaction

from .permissions import IsAdmin, IsOwnerProduct, IsOwnerShop, IsOwnerImageProduct, IsSeller
from .models import (Category, Shop, Product, ReviewProduct, ImageProduct, CommentProduct,
                     CrownProduct, ReviewShop, Cart, Order, HistorySearch)
from .serializer import (CategorySerializer, ShopSerializer, ProductSerializer,
                         ProductDetailSerializer, ReviewProductSerializer, ReviewShopSerializer,
                         ShopDetailSerializer, ImageProductSerializer, ProfileInfoSerializer,
                         CommentProductSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, CreateOrderSerializer,
                         HistorySearchSerializer,
                         CrownProductSerializer, CommentSerializer)

class ShopListCreateView(generics.ListCreateAPIView):
    serializer_class = ShopSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdmin | IsOwnerShop]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Shop.objects.none()
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
    
class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()
        return Category.objects.annotate(
            total_products=Count('category_products', distinct=True),
        )
    
    @swagger_auto_schema(tags=['Category'], consumes=['multipart/form-data']) 
    def get(self, request, *args, **kwargs):
        cache_key = 'category_list'
        data = cache.get(cache_key)
        if not data:
            serializer = self.get_serializer(self.get_queryset(), many=True)
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
    queryset = Category.objects.none()
    
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

class ShopListView(generics.ListAPIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Shop.objects.none()
        return Shop.objects.annotate(
            avg_crowns=Coalesce(
                Avg('products__product_crowns__crowns'),
                0,
                output_field=DecimalField()
            )
        ).select_related('seller')
    
    @swagger_auto_schema(tags=['Shop'], consumes=['multipart/form-data'])  
    def get(self, request, *args, **kwargs):
        cache_key = 'shop_list'
        data = cache.get(cache_key)
        if not data:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            data = serializer.data
            cache.set(cache_key, data, 60)
        return Response(data)
    
class ShopDetailView(generics.RetrieveAPIView):
    serializer_class = ShopDetailSerializer
    permission_classes = [permissions.AllowAny]  
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
        serializer_reviews = ReviewShopSerializer(
            context = {'user': request.user, 'shop': shop},
            data = {'user': request.user.id, 'shop': shop.id}
        )
        if serializer_reviews.is_valid():
            serializer_reviews.save()
        return Response(data)

class ShopCreateView(generics.CreateAPIView):
    serializer_class = ShopSerializer
    permission_classes = [IsAdmin | permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Shop.objects.none()
    
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

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        return Product.objects.annotate(
            avg_crowns=Coalesce(
                Avg('product_crowns__crowns'),
                0,
                output_field=DecimalField()
            )
        ).select_related('shop')
    
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def get(self, request, *args, **kwargs):
        cache_key = 'product_list'
        data = cache.get(cache_key)
        if not data:
            serializer = self.get_serializer(self.get_queryset(), many=True)
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
        
        serializer_reviews = None
        if request.user.is_authenticated:
            serializer_reviews = ReviewProductSerializer(
                context = {'user': request.user, 'product': product},
                data = {'user': request.user.id, 'product': product.id}
            )
            if serializer_reviews.is_valid():
                serializer_reviews.save()
        return Response(data)

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin | IsOwnerShop]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Product.objects.none()
    
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
    queryset = Product.objects.all()
    permission_classes = [IsAdmin | IsOwnerProduct]
    
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def delete(self, request, *args, **kwargs):
        cache.clear()
        return super().delete(request, *args, **kwargs)

class ProductImageAddView(generics.CreateAPIView):
    serializer_class = ImageProductSerializer
    permission_classes = [IsAdmin | IsSeller]
    queryset = ImageProduct.objects.none()
    
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, id=product_id)
        if not (request.user.role == 'AD' or request.user.is_staff or product.shop.seller == request.user):
            return Response(
                {'detail': 'You do not have permission to add images to this product.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product_id=product_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductImageDestroyView(generics.DestroyAPIView):
    serializer_class = ImageProductSerializer
    queryset = ImageProduct.objects.all()
    permission_classes = [IsAdmin | IsSeller]
    
    @swagger_auto_schema(tags=['Product'], consumes=['multipart/form-data'])
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user.role == 'AD' or request.user.is_staff or instance.product.shop.seller == request.user):
            return Response(
                {'detail': 'You do not have permission to delete this image.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)

class ProfileInfoView(generics.RetrieveAPIView):
    serializer_class = ProfileInfoSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = None
    
    @swagger_auto_schema(tags=['User Info'])   
    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class CommentsProduct(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentProductSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CommentProduct.objects.none()
        product_id = self.kwargs.get('pk')
        return CommentProduct.objects.filter(product_id=product_id)
    
    @swagger_auto_schema(tags=['Comments'])
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

class CommentsToProduct(generics.CreateAPIView):
    serializer_class = CommentProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CommentProduct.objects.none()
    
    @swagger_auto_schema(tags=['Commnets'],consumes=['multipart/form-data'])
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product_id=product_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentDestroyView(generics.DestroyAPIView):
    serializer_class = CommentProductSerializer
    queryset = CommentProduct.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['Comments'])
    def delete(self, request, *args, **kwargs):
        user = request.user
        comment = self.get_object()
        if user != comment.user:
            return Response({'detail': 'You do not have permission to delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

class CommentUpdateView(generics.UpdateAPIView):
    serializer_class = CommentProductSerializer
    queryset = CommentProduct.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put']
    
    @swagger_auto_schema(tags=['Comments'])
    def put(self, request, *args, **kwargs):
        user = request.user
        comment = self.get_object()
        if user != comment.user:
            return Response({'detail': 'You do not have permission to update this comment.'}, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.none()
    
    @swagger_auto_schema(tags=['Cart'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CartCreateView(generics.CreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.none()
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.none()
    
    @swagger_auto_schema(tags=['Cart'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.none()
    
    @swagger_auto_schema(tags=['Cart'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CartDestroyView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.none()
    
    @swagger_auto_schema(tags=['Cart'])
    def delete(self, request, *args, **kwargs):
        user = request.user
        cart = self.get_object()
        if user != cart.user:
            return Response({'detail': 'You do not have permission to delete this cart'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

class CartUpdateView(generics.UpdateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.none()
    
    @swagger_auto_schema(tags=['Cart'])
    def put(self, request, *args, **kwargs):
        user = request.user
        cart = self.get_object()
        if user != cart.user:
            return Response({'detail': 'You do not have permission to update this cart'}, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_authenticated:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.none()

class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.none()
    
    @transaction.atomic  
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({
            'message': 'Order created successfully',
            'order_id': order.id,
            'total_amount': order.total_amount
        }, status=status.HTTP_201_CREATED)

class HistoryUserView(generics.ListAPIView):
    serializer_class = HistorySearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return HistorySearch.objects.none()
        if self.request.user.is_authenticated:
            return HistorySearch.objects.filter(user=self.request.user)[:10]
        return HistorySearch.objects.none()
    
    @swagger_auto_schema(tags=['History'])
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

class HistoryCreateView(generics.CreateAPIView):
    serializer_class = HistorySearchSerializer
    permission_classes = [permissions.IsAuthenticated | permissions.AllowAny]
    queryset = HistorySearch.objects.none()
    
    @swagger_auto_schema(tags=['History'])
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

class HistoryDestroyView(generics.DestroyAPIView):
    serializer_class = HistorySearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = HistorySearch.objects.all()
    
    @swagger_auto_schema(tags=['History'])
    def delete(self, request, *args, **kwargs):
        user = request.user
        history = self.get_object()
        if user != history.user:
            return Response({'detail': 'You do not have permission to delete this history.'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

class CrownProductView(generics.CreateAPIView):
    serializer_class = CrownProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CrownProduct.objects.none()
    
    @swagger_auto_schema(tags=['Crowns'],consumes=['multipart/form-data'])
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('pk'))
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CommentProduct.objects.none()
        product_id = self.kwargs.get('product_id')
        return CommentProduct.objects.filter(product_id=product_id)
    
    @swagger_auto_schema(tags=['Product'],consumes=['multipart/form-data'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CommentProduct.objects.none()
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(user=self.request.user, product=product)

class CommentDetailView(generics.RetrieveAPIView):
    queryset = CommentProduct.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['Comments'],consumes=['multipart/form-data'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CommentUpdateView(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CommentProduct.objects.none()
        if self.request.user.is_authenticated:
            return CommentProduct.objects.filter(user=self.request.user)
        return CommentProduct.objects.none()
    
    @swagger_auto_schema(tags=['Comments'], consumes=['multipart/form-data'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

class CommentDestroyView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CommentProduct.objects.none()
        if self.request.user.is_authenticated:
            return CommentProduct.objects.filter(user=self.request.user)
        return CommentProduct.objects.none()
    
    @swagger_auto_schema(tags=['Comments'], consumes=['multipart/form-data'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class MyCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return CommentProduct.objects.none()
        if self.request.user.is_authenticated:
            return CommentProduct.objects.filter(user=self.request.user)
        return CommentProduct.objects.none()
    
    @swagger_auto_schema(tags=['Prodile Info'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)