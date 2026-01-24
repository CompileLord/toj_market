from rest_framework import serializers
from django.db.models import F
from .models import (
    Category, Product, ImageProduct, CommentProduct, CrownProduct,
    ReviewProduct, Shop, User, HistorySearch, Cart, Order, ReviewShop
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'avatar')
        read_only_fields = ('id',)
    
    def validate_title(self, value):
        if Category.objects.filter(title__iexact=value).exists():
            raise serializers.ValidationError('This title name already exists')
        return value

class ShopSerializer(serializers.ModelSerializer):
    seller_full_name = serializers.SerializerMethodField()
    avg_crowns = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    total_products = serializers.IntegerField(read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Shop
        fields = ('id', 'seller_full_name','title', 'bio', 'avatar', 'avg_crowns', 
                  'total_products', 'total_orders', 'review_count')
        read_only_fields = ('id', 'seller_full_name', 'review_count')
    
    def validate(self, attrs):
        user = self.context['request'].user
        if Shop.objects.filter(seller=user).exists():
            raise serializers.ValidationError('You already have a shop')
        if user.telegram_id is None:
            raise serializers.ValidationError('You must set your telegram id')
        return attrs


    def get_seller_full_name(self, obj):
        return f'{obj.seller.first_name} {obj.seller.last_name}'.strip()
    
    def create(self, validated_data):
        user = self.context['request'].user
        user.role = 'SL'
        user.save()
        return Shop.objects.create(seller=user, **validated_data)

class ImageProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ImageProduct
        fields = ('id', 'product', 'image', 'is_main_image')
        read_only_fields = ('id',)

class ProductSerializer(serializers.ModelSerializer):
    avg_crowns = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'price', 'quantity', 'discount', 
                   'shop', 'category', 'views_count', 'avg_crowns', 'main_image')
        read_only_fields = ('id', 'shop', 'views_count', 'main_image', 'avg_crowns')
        extra_kwargs = {'description': {'write_only': True}, 'quantity': {'write_only': True}}

    
    def get_main_image(self, obj):
        image = obj.images.filter(is_main_image=True).first()
        if image:
            return image.image.url
        return None


    def create(self, validated_data):
        user = self.context['request'].user
        try:
            user_shop = Shop.objects.get(seller=user)
        except Shop.DoesNotExist:
            raise serializers.ValidationError("You must create a shop first.")
            
        return Product.objects.create(shop=user_shop, **validated_data)

class CommentProductSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = CommentProduct
        fields = ('id', 'text', 'product', 'user')
        read_only_fields = ('id', 'product', 'user')

class ProductDetailSerializer(serializers.ModelSerializer):
    comments = CommentProductSerializer(many=True, read_only=True)
    images = ImageProductSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'price', 'quantity', 'discount', 
                  'created_at', 'shop', 'category', 'views_count', 'comments', 'images')
        read_only_fields = ('id', 'shop', 'views_count', 'created_at', 'comments', 'images')

class HistorySearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = HistorySearch
        fields = ('user', 'text', 'datetime')
        read_only_fields = ('user', 'datetime')

    def create(self, validated_data):
        user = self.context['request'].user
        return HistorySearch.objects.create(user=user, **validated_data)

class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ('id', 'user', 'product', 'count')
        read_only_fields = ('id', 'user', 'product')
    
    def validate(self, attrs):
        product = attrs['product']
        count = attrs['count']
        if product.quantity < count:
            raise serializers.ValidationError('The count can not be more then quantity of the product')
        cart = Cart.objects.filter(id=product, user=attrs['user'])
        if cart.exists():
            raise serializers.ValidationError('You already have this product in your cart')
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        product = self.validated_data.get('product')
        count = self.validated_data.get('count')
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product = product,
            defaults={'count': count}
        )
        if not created:
            cart_item.count += count
            cart_item.save()
        return cart_item



class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('id', 'user', 'product', 'count', 'total', 'created_at')
    
    def create(self, validated_data):
        user = self.context['request'].user
        return Order.objects.create(user=user, **validated_data)


class CrownProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CrownProduct
        fields = ('id', 'user', 'crowns', 'product')
        read_only_fields = ('id', 'user', 'product')
    
    def validate(self, attrs):
        user = self.context['request'].user
        product = attrs.get('product')
        crown_instance = CrownProduct.objects.filter(user=user, product=product)
        if crown_instance:
            self.instance = crown_instance
        return attrs   
    
    def create(self, validated_data):
        user = self.context['request'].user
        return CrownProduct.objects.create(user=user, **validated_data)

class ReviewProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewProduct
        fields = ('id', 'product', 'user')
        read_only_fields = ('id','product', 'user')

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data.get('product')

        review, created = ReviewProduct.objects.update_or_create(
            user=user,
            product=product
        )
        if created:
            product.views_count = F('views_count') + 1
            product.save()
            product.refresh_from_db()
        
        return review

class ReviewShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewShop
        fields = ('id', 'user', 'shop')
        read_only_fields = ('id', 'user', 'shop')
    
    def create(self, validated_data):
        user = self.context['request'].user
        shop = validated_data.get('shop')

        review, created = ReviewShop.objects.update_or_create(
            user = user,
            shop=shop
        )
        if created:
            shop.review_count = F('review_count') + 1
            shop.save()
            shop.refresh_from_db
        
        return review
    
    
        


        
    








