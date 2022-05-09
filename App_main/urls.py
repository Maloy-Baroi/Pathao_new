from django.urls import path
from App_main import views

app_name = 'App_main'

urlpatterns = [
    path('', views.customer_dashboard, name='customer_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart-view/', views.cart_showcase, name='cart-view'),
    path('update-cart/', views.cart_update, name='update-cart'),
    path('checkout/', views.checkout, name='checkout-page'),
    path('purchase/', views.purchase_action, name='purchase'),
    path('profile-view/', views.profile_view, name='profile-view'),
    # path('setiings/', views.profile_settings, name='settings'),
    path('previous-order/', views.previous_orders, name='previous-order'),
    #     Admin
    path('register-with-admin/', views.register_user_by_admin, name='register-with-admin'),
    path('update-product/', views.update_product, name='update-product'),
    path('delete-product/<int:product_key>/', views.delete_product, name='delete-product'),
    path('add-new-product/', views.add_new_product, name='add-new-product'),
    path('add-new-category/', views.add_category, name='add-new-category'),
    path('delete-shortage-record/<int:table_key>/', views.delete_shortage_table, name='delete-shortage-record'),
    path('update-order-status/', views.update_order_status, name='update-order-status'),
    path('update-order-item-quantity/', views.admin_updates_asking_quantity, name='update-order-item-quantity'),
    path('invoice-generator/<int:OrderID>/', views.admin_generates_invoice, name='invoice-generator')
]
