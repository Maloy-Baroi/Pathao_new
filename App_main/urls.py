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
    path('invoice-generator/<int:OrderID>/', views.admin_generates_invoice, name='invoice-generator'),
    #     Admin
    path('boss-admin/', views.boss_admin_dashboard, name='boss_admin_dashboard'),
    path('boss-register-with-admin/', views.register_user_by_boss_admin, name='boss-register-with-admin'),
    path('boss-update-product/', views.boss_update_product, name='boss-update-product'),
    path('boss-delete-product/<int:product_key>/', views.boss_delete_product, name='boss-delete-product'),
    path('boss-add-new-product/', views.boss_add_new_product, name='boss-add-new-product'),
    path('boss-add-new-category/', views.boss_add_category, name='boss-add-new-category'),
    path('boss-delete-shortage-record/<int:table_key>/', views.boss_delete_shortage_table,
         name='boss-delete-shortage-record'),
    path('boss-update-order-status/', views.boss_update_order_status, name='boss-update-order-status'),
    path('boss-update-order-item-quantity/', views.boss_admin_updates_asking_quantity,
         name='boss-update-order-item-quantity'),
    path('boss-invoice-generator/<int:OrderID>/', views.boss_admin_generates_invoice, name='boss-invoice-generator')
]
