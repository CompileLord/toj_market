from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, CategoryPutView, CategoryDestroyView, CategoryCreateView,
    ShopListView, ShopDetailView, ShopCreateView, ShopPutView, ShopDestroyView,
    ProductListView, ProductCreateView, ProductPutView, ProductDestroyView, ProductDetailView, ProductImageAddView, ProductImageDestroyView,
    ProfileInfoView, CartUserItemsView, DeleteItemsCartView, OrderItemsView, OrderAddItemView, OrderDestruyView,
    HistoryUserView, HistoryCreateView, HistoryDestroyView, CartItemAddView

)

app_name = 'market'

urlpatterns = [

    # -- Profile info
    path('api/profile-info/', ProfileInfoView.as_view(), name='profile-info'),

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
    path('api/products/get-by-id/<int:pk>', ProductDetailView.as_view(), name='product-detail'),
    path('api/products/get-all-products/', ProductListView.as_view(), name='product-list'),
    path('api/products/create/', ProductCreateView.as_view(), name='product-create'),
    path('api/products/<int:pk>/update/', ProductPutView.as_view(), name='product-update'),
    path('api/products/<int:pk>/destroy/', ProductDestroyView.as_view(), name='product-delete'),
    path('api/products/<int:pk>/add-image/', ProductImageAddView.as_view(), name='product-image-add'),
    path('api/products/<int:pk>/delete-image/', ProductImageDestroyView.as_view(), name='product-image-delete'),

    # -- Cart
    path('api/cart/get-all-items/', CartUserItemsView.as_view(), name='cart-items'),
    path('api/cart/add-item/<int:pk>', CartItemAddView.as_view(), name='cart-add'),
    path('api/cart/delete-item/<int:pk>', DeleteItemsCartView.as_view(), name='cart-delete'),

    # -- Order 
    path('api/order/get-all-items/', OrderItemsView.as_view(), name='order-items'),
    path('api/order/add-item/<int:pk>', OrderAddItemView.as_view(), name='order-add'),
    path('api/order/delete-item/<int:pk>', OrderDestruyView.as_view(), name='order-delete'),

    # -- History       
    path('api/history/get-all-items/', HistoryUserView.as_view(), name='history-items'),
    path('api/history/add-item/', HistoryCreateView.as_view(), name='history-add'),
    path('api/history/delete-item/<int:pk>', HistoryDestroyView.as_view(), name='history-delete'),



  
    
]



