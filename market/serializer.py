from rest_framework import serializers
from django.db.models import F, Count
from django.db import transaction
from accounts.serializers import GetUserInfoSerialzer
from decimal import  Decimal

from .models import (
    Category, Product, ImageProduct, CommentProduct, CrownProduct,
    ReviewProduct, Shop, User, HistorySearch, Cart, Order, ReviewShop, OrderItem
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
    avg_crowns = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Shop
        fields = ('id', 'title', 'bio', 'avatar', 'avg_crowns',  'review_count')
        read_only_fields = ('id',  'review_count')
    
    def validate(self, attrs):
        user = self.context['request'].user
        if not user.telegram_id :
            raise serializers.ValidationError('You must set your telegram id')
        return attrs

    
    def create(self, validated_data):
        user = self.context['request'].user
        user.role = 'SL'
        user.save()
        if Shop.objects.filter(seller=user).exists():
            raise serializers.ValidationError('You already have a shop')
        return Shop.objects.create(seller=user, **validated_data)


class ShopDetailSerializer(serializers.ModelSerializer):
    seller_full_name = serializers.SerializerMethodField()
    avg_crowns = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    total_products = serializers.IntegerField(read_only=True)
    total_orders = serializers.IntegerField(read_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)
    last_added_product = serializers.SerializerMethodField()  
    most_popular_products = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ('id', 'seller_full_name','title', 'bio', 'avatar', 'avg_crowns', 
                  'total_products', 'total_orders', 'review_count', 'last_added_product', 
                  'most_popular_products', 'created_at')
        read_only_fields = ('id', 'seller_full_name', 'review_count')
    
    def get_seller_full_name(self, obj):
        return f'{obj.seller.first_name} {obj.seller.last_name}'.strip()

    def get_last_added_product(self, obj):
        last_product = obj.products.order_by('-created_at').first()
        return ProductSerializer(last_product).data if last_product else None

    def get_most_popular_products(self, obj):
        most_popular_products = obj.products.annotate(total_orders=Count('orders')).order_by('-total_orders')[:6]
        return ProductSerializer(most_popular_products, many=True).data

    def create(self, validated_data):
        user = self.context['user']
        shop = self.context['prodshopuct']

        review, created = ReviewShop.objects.update_or_create(
            user=user,
            shop=shop
        )
        if created:
            shop.review_count = F('review_count') + 1
            shop.save()
        
        return review
        

class ImageProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ImageProduct
        fields = ('id', 'product', 'image', 'is_main_image')
        read_only_fields = ('id', 'product')
    


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
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url # если request почему-то нет
        return None


    def create(self, validated_data):
        user = self.context['request'].user
        user_shop = Shop.objects.filter(seller=user).first()
        if not user_shop:
            raise serializers.ValidationError("You must create a shop first.")
            
        return Product.objects.create(shop=user_shop, **validated_data)

class CommentProductSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.first_name')

    class Meta:
        model = CommentProduct
        fields = ('id', 'text', 'product', 'user')
        read_only_fields = ('id',  'user')
    
    def validate(self, attrs):
        product = attrs.get('product')
        user = self.context['request'].user
        
        if CommentProduct.objects.filter(product=product, user=user).count() > 3:
            raise serializers.ValidationError("You have already 3 comments for this product")
        
        if not Product.objects.filter(id=product.id).exists():
            raise serializers.ValidationError("This product does not exist.")
        
        return attrs

    
    

class ProductDetailSerializer(serializers.ModelSerializer):
    comments = CommentProductSerializer(many=True, read_only=True)
    images = ImageProductSerializer(many=True, read_only=True)
    shop_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'price', 'quantity', 'discount', 
                  'created_at', 'shop', 'category', 'views_count', 'comments', 
                  'images', 'shop_info', 'category_info')
        read_only_fields = ('id', 'shop', 'views_count', 'created_at', 
                           'comments', 'images', 'shop_info', 'category_info')
    
    def get_shop_info(self, obj):
        return ShopSerializer(obj.shop).data if obj.shop else None
    
    def get_category_info(self, obj):
        return {
            'id': obj.category.id,
            'title': obj.category.title,
            'avatar': obj.category.avatar.url if obj.category.avatar else None
        } if obj.category else None
    
class HistorySearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = HistorySearch
        fields = ('user', 'text', 'datetime')
        read_only_fields = ('user', 'datetime')

    def create(self, validated_data):
        user = self.context['request'].user
        return HistorySearch.objects.create(user=user, **validated_data)


class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'product', 'quantity', 'created_at', 'updated_at', 'product_name', 'product_price', 'total_price')
        read_only_fields = ('id', 'user')
    
    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        user = self.context['request'].user
        
        existing_quantity = 0
        if Cart.objects.filter(user=user, product=product).exists():
            existing_quantity = Cart.objects.get(user=user, product=product).quantity
            
        if product.quantity < (quantity + existing_quantity):
            raise serializers.ValidationError(f'Not enough quantity! Available: {product.quantity}')
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data.get('product')
        quantity = validated_data.get('quantity')
        
        try:
            cart_item = Cart.objects.get(user=user, product=product)
            cart_item.quantity = F('quantity') + quantity
            cart_item.save()
            cart_item.refresh_from_db()  
        except Cart.DoesNotExist:
            cart_item = Cart.objects.create(
                user=user,
                product=product,
                quantity=quantity
            )
        
        return cart_item

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.title', read_only=True)
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'quantity', 'product_name', 'price_at_purchase')
        read_only_fields = ('id', 'order', 'product', 'price_at_purchase')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = Order
        fields = ('id', 'user', 'items', 'status', 'status_display', 'created_at', 'total_amount')
        read_only_fields = ('id', 'user', 'items', 'created_at', 'total_amount')


class CreateOrderSerializer(serializers.Serializer):
    cart_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="IDs of products to buy. If empty, all items in cart will be processed."
    )

    def validate(self, data):
        user = self.context['request'].user
        cart_ids = data.get('cart_ids')
        queryset = Cart.objects.filter(user=user).select_related('product')

        if cart_ids:
            cart_items = queryset.filter(id__in=cart_ids)
            if cart_items.count() != len(cart_ids):
                raise serializers.ValidationError("Some items were not found in your cart.")
        else:
            cart_items = queryset

        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty.")
        for item in cart_items:
            if item.product.quantity < item.quantity:
                raise serializers.ValidationError(
                    f"Product '{item.product.title}' only has {item.product.quantity} units left."
                )

        data['cart_items'] = cart_items
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = validated_data['cart_items']

        main_product = cart_items.first().product

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                product=main_product,
                total_amount=0
            )

            total_amount = 0
            order_items_list = []

            for cart_item in cart_items:
                product = cart_item.product
                product = Product.objects.select_for_update().get(id=product.id)

                if product.quantity < cart_item.quantity:
                    raise serializers.ValidationError(f"Not enough stock for {product.title}")

                discount_val = getattr(product, 'discount', 0) or 0
                discount_pct = Decimal(str(discount_val))
                
                unit_price = product.price
                unit_discount = unit_price * (discount_pct / Decimal('100'))
                unit_price_after_discount = unit_price - unit_discount
                
                item_total = unit_price_after_discount * cart_item.quantity
                total_amount += item_total

                order_items_list.append(
                    OrderItem(
                        order=order,
                        product=product,
                        quantity=cart_item.quantity,
                        price_at_purchase=unit_price_after_discount
                    )
                )
                product.quantity -= cart_item.quantity
                product.save()
            OrderItem.objects.bulk_create(order_items_list)
            order.total_amount = total_amount
            order.save()
            from .signals import start_bot_notification
            transaction.on_commit(lambda: start_bot_notification(order))
            cart_items.delete()

        return order
    




class CrownProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CrownProduct
        fields = ('id', 'user', 'crowns', 'product')
        read_only_fields = ('id', 'user', 'product')
    
    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data.get('product')
        crowns = validated_data.get('crowns')
        crown_instance, created = CrownProduct.objects.update_or_create(
            user=user,
            product=product,
            defaults={'crowns': crowns}
        )
        return crown_instance

class ReviewProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewProduct
        fields = ('id', 'product', 'user')
        read_only_fields = ('id','product', 'user')

    def create(self, validated_data):
        user = self.context['user']
        product = self.context['product']

        review, created = ReviewProduct.objects.update_or_create(
            user=user,
            product=product
        )
        if created:
            product.views_count = F('views_count') + 1
            product.save()
        
        return review

class ReviewShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewShop
        fields = ('id', 'user', 'shop')
        read_only_fields = ('id', 'user', 'shop')
    
    def create(self, validated_data):
        user = self.context['user']
        shop = self.context['shop']

        review, created = ReviewShop.objects.update_or_create(
            user = user,
            shop=shop
        )
        if created:
            shop.review_count = F('review_count') + 1
            shop.save()
        
        return review
    

class ProfileInfoSerializer(serializers.Serializer):    
    user_info = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()  
    last_added_cart_items = serializers.SerializerMethodField()  
    
    
    def get_user_info(self, obj):
        user = self.context['request'].user
        return GetUserInfoSerialzer(user).data
    
    def get_total_orders(self, obj):  
        user = self.context['request'].user
        return Order.objects.filter(user=user).count()
    
    def get_last_added_cart_items(self, obj):  
        user = self.context['request'].user
        return CartSerializer(Cart.objects.filter(user=user).order_by('-created_at')[:4], many=True).data


class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.first_name', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    
    class Meta:
        model = CommentProduct
        fields = ['id', 'text', 'product', 'user', 'user_name', 'user_id', 'created_at']
        read_only_fields = ['id', 'user', 'user_name', 'user_id', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    



# #--- Search serializer
#
# class MainPageSerializer(serializers.Serializer):
#     popular_categories = CategorySerializer(many=True)
#     popular_products = ProductSerializer(many=True)
#     featured_products = ProductSerializer(many=True)
#     last_added_products = ProductSerializer(many=True)

    

    



    
    
        


        
    








