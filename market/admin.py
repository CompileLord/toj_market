from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import *
User = get_user_model()



# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Shop)
admin.site.register(ImageProduct)
admin.site.register(User)