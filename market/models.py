from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()








class Category(models.Model):
    title = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='category_avatars/')
    is_deleted = models.BooleanField(default=False)

    def delete(self):
        self.is_deleted = True
        self.save()


class Shop(models.Model):
    seller = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='shop_avatars/')
    review_count = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)



class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    discount = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_products')
    is_deleted = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)



class ImageProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_additional_images/')
    is_main_image = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if self.is_main_image: 
            ImageProduct.objects.filter(product=self.product).update(is_main_image=False)
        super().save(*args, **kwargs)


class CommentProduct(models.Model):
    text = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')


class CrownProduct(models.Model):
    class CrownChoices(models.IntegerChoices):
        ONE = 1, 'One crown'
        TWO = 2, 'Two crowns'
        THREE = 3, 'Three crowns'
        FOUR = 4, 'Four crowns'
        FIVE = 5, 'Five crowns'
    crowns = models.IntegerField(choices=CrownChoices, default=CrownChoices.ONE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_crowns')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class HistorySearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')
    text = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now_add=True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    class Meta:
        unique_together = ('user', 'product')

    @property
    def totall(self):
        return self.product.price * self.count



class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PN', 'Pending'
        PAID = 'PD', 'Paid'
        SHIPPED = 'SH', 'Shipped'
        DELIVERED = 'DL', 'Delivered'
        CANCELLED = 'CN', 'Cancelled'
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PENDING)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_items')
    count = models.IntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'product')



class ReviewProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')


class ReviewShop(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_reviews')




