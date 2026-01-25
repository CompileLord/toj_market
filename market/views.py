from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from drf_yasg.utils import swagger_auto_schema

from django.db.models import Avg, Count, DecimalField
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from django.core.cache import cache

from .permissions import IsAdmin, IsOwnerProduct, IsOwnerShop, IsOwnerImageProduct, IsSeller
from .models import (Category, Shop, Product, ReviewProduct, ImageProduct, CommentProduct,
                     CrownProduct, ReviewShop, Cart, Order, HistorySearch)
from .serializer import (CategorySerializer, ShopSerializer, ProductSerializer,
                         ProductDetailSerializer, ReviewProductSerializer, ReviewShopSerializer,
                         ShopDetailSerializer, ImageProductSerializer, ProfileInfoSerialzer,
                         CommentProductSerializer, CartSerializer, OrderSerializer, HistorySearchSerializer)




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
            print(serializer_reviews.data)

        
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
        if request.user.is_authenticated:
            serializer_reviews = ReviewProductSerializer(
                context = {'user': request.user, 'product': product},
                data = {'user': request.user.id, 'product': product.id}
            )
            if serializer_reviews.is_valid():
                serializer_reviews.save()
                print(serializer_reviews.data)
        data['reviews'] = serializer_reviews.data
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

class ProductImageAddView(generics.CreateAPIView):
    serializer_class = ImageProductSerializer
    permission_classes = [IsAdmin | IsSeller]
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


    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ImageProduct.objects.none()

        product_id = self.kwargs.get('pk') 
        return ImageProduct.objects.filter(product_id=product_id)

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



# -- Profile info
class ProfileInfoView(generics.RetrieveAPIView):
    serializer_class = ProfileInfoSerialzer
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(tags=['User Info'])   
    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)



# ---- Comments

class CommentsProduct(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentProductSerializer
    @swagger_auto_schema(tags=['Comments'])
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        serializer = self.get_serializer(CommentProduct.objects.filter(product_id=product_id), many=True)
        return Response(serializer.data)

class CommentsToProduct(generics.CreateAPIView):
    serializer_class = CommentProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(tags=['Comments'])
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        comments = CommentProduct.objects.filter(product_id=product_id)
    
    @swagger_auto_schema(tags=['Commnets'],consumes=['multipart/form-data'])
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product_id=product_id)

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
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put']
    @swagger_auto_schema(tags=['Comments'])
    def put(self, request, *args, **kwargs):
        user = request.user
        comment = self.get_object()
        if user != comment.user:
            return Response({'detail': 'You do not have permission to update this comment.'}, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)


# --- Cart logic

class CartUserItemsView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(tags=['Cart'])
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(Cart.objects.filter(user=user), many=True)
        return Response(serializer.data)

class CartItemAddView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    @swagger_auto_schema(tags=['Cart'])
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('pk'))
        serializer = self.get_serializer(product)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteItemsCartView(generics.DestroyAPIView):
    serializer_class = CommentProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()
    @swagger_auto_schema(tags=['Cart'])
    def delete(self, request, *args, **kwargs):
        user = request.user
        cart_item = get_object_or_404(Cart, pk=kwargs.get('pk'))
        if user != cart_item.user:
            return Response({'detail': 'You do not have permission to delete this item from your cart.'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


# --- Order items

class OrderItemsView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(tags=['Order'])
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(Order.objects.filter(user=user), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderAddItemView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(tags=['Order'])
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs.get('pk'))
        serializer = self.get_serializer(product)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderDestruyView(generics.DestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()
    @swagger_auto_schema(tags=['Order'])
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        order = self.get_object()
        if user != order.user:
            return Response({'detail': 'You do not have permission to delete this order.'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


# --- History

class HistoryUserView(generics.ListAPIView):
    serializer_class = HistorySearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(tags=['History'])
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(HistorySearch.objects.filter(user=user)[:10], many=True)
        return Response(data)

class HistoryCreateView(generics.CreateAPIView):
    serializer_class = HistorySearchSerializer
    permission_classes = [permissions.IsAuthenticated | permissions.AllowAny]
    @swagger_auto_schema(tags=['History'])
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)

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








        








    

    








    



        


