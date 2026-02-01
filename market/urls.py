from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, CategoryPutView, CategoryDestroyView, CategoryCreateView,
    ShopListView, ShopDetailView, ShopCreateView, ShopPutView, ShopDestroyView, GetMyShop,
    ProductListView, ProductCreateView, ProductPutView, ProductDestroyView, ProductDetailView, ProductImageAddView, ProductImageDestroyView,
    ProfileInfoView, CartCreateView, CartListView, CartDetailView, CartDestroyView, CartUpdateView,
    OrderListView, OrderDetailView, CreateOrderView,  CommentDestroyView, CommentUpdateView, CommentListView,
    MyCommentsListView, CommentDetailView,
    HistoryUserView, HistoryCreateView, HistoryDestroyView, CrownProductView,
    CommentsProduct, CommentsToProduct,
    # AISearchView
)

app_name = 'market'

urlpatterns = [
    # ---- Profile info
    path('profile-info/', ProfileInfoView.as_view(), name='profile-info'),
    path('profile-info/my-last-comments/', MyCommentsListView.as_view(), name='my-last-comments'),

    # ----- Category api
    path('categories/get-all-categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/get-by-id/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:pk>/update/', CategoryPutView.as_view(), name='category-update'),
    path('categories/<int:pk>/destroy/', CategoryDestroyView.as_view(), name='category-delete'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),

    # ----- Shop api
    path('shops/get-all-shops/', ShopListView.as_view(), name='shop-list'),
    path('shops/get-by-id/<int:pk>/', ShopDetailView.as_view(), name='shop-detail'),
    path('shops/<int:pk>/update/', ShopPutView.as_view(), name='shop-update'),
    path('shops/<int:pk>/destroy/', ShopDestroyView.as_view(), name='shop-delete'),
    path('shops/create/', ShopCreateView.as_view(), name='shop-create'),
    path('shops/get-my-shop/', GetMyShop.as_view(), name='get-my-shop'),


    #  ----- Product api
    path('products/get-all-products/', ProductListView.as_view(), name='product-list'),
    path('products/get-by-id/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', ProductPutView.as_view(), name='product-update'),
    path('products/<int:pk>/destroy/', ProductDestroyView.as_view(), name='product-delete'),
    path('products/<int:pk>/add-image/', ProductImageAddView.as_view(), name='product-image-add'),
    path('products/delete-image/<int:pk>/', ProductImageDestroyView.as_view(), name='product-image-delete'),

    # ----- Cart
    path('cart/get-all-items/', CartListView.as_view(), name='cart-list'),
    path('cart/add-item/', CartCreateView.as_view(), name='cart-add'),
    path('cart/delete-item/<int:pk>/', CartDestroyView.as_view(), name='cart-delete'),
    path('cart/update-item/<int:pk>/', CartUpdateView.as_view(), name='cart-update'),
    path('cart/get-item/<int:pk>/', CartDetailView.as_view(), name='cart-detail'),

    # ----- Order 
    path('order/get-all-orders/', OrderListView.as_view(), name='order-list'),
    path('order/create/', CreateOrderView.as_view(), name='order-create'),
    path('order/get-by-id/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    
    # -- History
    path('history/get-all-items/', HistoryUserView.as_view(), name='history-list'),
    path('history/add-item/', HistoryCreateView.as_view(), name='history-add'),
    path('history/delete-item/<int:pk>/', HistoryDestroyView.as_view(), name='history-delete'),

    # -- Crowns
    path('crowns/add/<int:pk>/', CrownProductView.as_view(), name='crown-add'),

    # # -- AI Search
    # path('ai-search/', AISearchView.as_view(), name='ai-search'),

    # -- Comments
    path('comments/products/<int:pk>/', CommentsProduct.as_view(), name='product-comments-list'),
    path('comments/products/<int:pk>/add/', CommentsToProduct.as_view(), name='product-comment-add'),
    path('comments/<int:pk>/delete/', CommentDestroyView.as_view(), name='comment-delete'),
    path('comments/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),
    path('comments/product/<int:product_id>/', CommentListView.as_view(), name='comment-list'),
    path('comments/<int:pk>/detail/', CommentDetailView.as_view(), name='comment-detail'),



]