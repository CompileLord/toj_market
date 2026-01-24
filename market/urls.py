from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, CategoryPutView, CategoryDestroyView, CategoryCreateView,
    ShopListView, ShopDetailView, ShopCreateView, ShopPutView, ShopDestroyView,
    ProductListView, ProductCreateView, ProductPutView, ProductDestroyView, ProductImageView

)

app_name = 'market'

urlpatterns = [
    # -- Category api
    path('api/categories/get-all-categories/', CategoryListView.as_view(), name='category-list'),
    path('api/categories/get-get-by-id/<int:pk>', CategoryDetailView.as_view(), name='category-create'),
    path('api/categories/<int:pk>/update/', CategoryPutView.as_view(), name='category-update'),
    path('api/categories/<int:pk>/destroy/', CategoryDestroyView.as_view(), name='category-delete'),
    path('api/categories/create/', CategoryCreateView.as_view(), name='category-create'),

    # -- Shop api
    path('api/shops/get-all-shops/', ShopListView.as_view(), name='shop-list'),
    path('api/shops/get-get-by-id/<int:pk>', ShopDetailView.as_view(), name='shop-create'),
    path('api/shops/<int:pk>/update/', ShopPutView.as_view(), name='shop-update'),
    path('api/shops/<int:pk>/destroy/', ShopDestroyView.as_view(), name='shop-delete'),
    path('api/shops/create/', ShopCreateView.as_view(), name='shop-create'),

    # -- Product api
    path('api/products/get-all-products/', ProductListView.as_view(), name='product-list'),
    path('api/products/create/', ProductCreateView.as_view(), name='product-create'),
    path('api/products/<int:pk>/update/', ProductPutView.as_view(), name='product-update'),
    path('api/products/<int:pk>/destroy/', ProductDestroyView.as_view(), name='product-delete'),



  
    
]



