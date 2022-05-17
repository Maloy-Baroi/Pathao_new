import uuid

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Group

# Create your views here.
from django.urls import reverse

from App_auth.forms import SignUpForm
from App_auth.models import Profile, User
from App_auth.views import is_customer, is_admin, is_boss_admin
from App_main.forms import BillingForm, ProfileForm, ProductModelForm
from App_main.models import ProductModel, Cart, Order, BillingAddress, ShortageOfProduct, CategoryModel


@login_required
@user_passes_test(is_customer)
def customer_dashboard(request):
    c = Cart.objects.filter(user=request.user)
    products = ProductModel.objects.all()
    total_cart = Cart.objects.filter(user=request.user, purchased=False)
    cart_prod = [x.item.product_name for x in total_cart]
    print(cart_prod)
    content = {
        'products': products,
        'cart': total_cart,
        'prod_name': cart_prod
    }
    return render(request, 'App_main/customer_dashboard.html', context=content)


@login_required
@user_passes_test(is_customer)
def add_to_cart(request):
    pk = request.POST.get('product_id')
    quantity = int(request.POST.get('product_asking_quantity'))
    prod = ProductModel.objects.get(id=pk)
    try:
        cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
        cart_item.quantity += quantity
        cart_item.save()
    except:
        cart_item = Cart.objects.create(user=request.user, item=prod, quantity=quantity, purchased=False)
        cart_item.save()
    return HttpResponseRedirect(reverse('App_main:customer_dashboard'))


@login_required
@user_passes_test(is_customer)
def cart_showcase(request):
    carts = Cart.objects.filter(user=request.user, purchased=False)
    content = {
        'carts': carts
    }
    return render(request, 'App_main/cartView.html', context=content)


@login_required
@user_passes_test(is_customer)
def cart_update(request):
    pk = request.POST.get('product_id')
    quantity = int(request.POST.get('new_asking_quantity'))
    prod = ProductModel.objects.get(id=pk)
    cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
    cart_item.quantity = quantity
    cart_item.save()
    return HttpResponseRedirect(reverse('App_main:cart-view'))


def total_price_count(List, total):
    if len(List) == 0:
        return total
    else:
        i = List[0]
        total += i.quantity * i.item.price_per_unit
        List.remove(i)
        return total_price_count(List, total)


@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = BillingForm(instance=saved_address)
    if request.method == "POST":
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)
            messages.info(request, f"Shipping address saved!")

    cartItems = Cart.objects.filter(user=request.user, purchased=False)
    orderTotal = total_price_count(list(cartItems), 0)
    content = {
        'form': form,
        'cartItems': cartItems,
        'orderTotal': orderTotal,
        'saved_address': saved_address
    }
    return render(request, 'App_main/checkout.html', context=content)


def add_to_order(cart, order, total):
    if len(cart) == 0:
        return order
    else:
        i = cart[0]
        order.order_items.add(i)
        order.ordered = True
        order.payment_id = str(i.user)
        order.status = "Processing"
        order.order_id = str(i.user) + "-" + str(order.id)
        order.total_price = total
        cart.remove(i)
        return add_to_order(cart, order, total)


def delete_list(l_Delete):
    if len(l_Delete) == 0:
        return 0
    else:
        l_Delete[0].delete()
        delete_list(l_Delete)


@login_required
def purchase_action(request):
    order = Order.objects.create(user=request.user)
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    total = total_price_count(list(cart_items), 0)
    add_to_order(list(cart_items), order, total).save()
    for item in cart_items:
        product = ProductModel.objects.get(id=item.item.id)
        if product.No_of_available < item.quantity:
            shortage = ShortageOfProduct(product=product)
            shortage.storageAmount = item.quantity - product.No_of_available
            shortage.save()
            product.No_of_available = 0
        else:
            product.No_of_available -= item.quantity
        product.save()
        item.purchased = True
        item.save()
        orderDelete = Order.objects.filter(user=request.user, payment_id=None)
        delete_list(orderDelete)

    return HttpResponseRedirect(reverse('App_main:customer_dashboard'))


def profile_view(request):
    profile = Profile.objects.get_or_create(user=request.user)[0]
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            thisForm = form.save(commit=False)
            thisForm.user = request.user
            thisForm.save()
            return HttpResponseRedirect(reverse('App_main:profile-view'))

    content = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'App_main/profile_view.html', context=content)


# def profile_settings(request):
#     profile = Profile.objects.get(user=request.user)
#     form = ProfileForm(instance=profile)
#     if request.method == 'POST':
#         form = ProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             thisForm = form.save(commit=False)
#             thisForm.user = request.user
#             thisForm.save()
#             return HttpResponseRedirect(reverse('App_main:settings'))
#
#     content = {
#         'form': form
#     }
#     return render(request, 'App_main/settings.html', context=content)


@login_required
@user_passes_test(is_customer)
def previous_orders(request):
    previous_order = Order.objects.filter(user=request.user)
    content = {
        'previous_orders': previous_order
    }
    return render(request, 'App_main/previous_orders.html', context=content)


# <! ------- Admin Start ------->
def checkAdmin(userList, x_result):
    if len(userList) == 0:
        return x_result
    else:
        if is_admin(userList[0]):
            pass
        else:
            x_result.append(userList[0])
        userList.remove(userList[0])
        return checkAdmin(userList, x_result)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    form = SignUpForm()
    total_user = User.objects.filter(is_superuser=False)
    allCustomers = checkAdmin(list(total_user), [])
    total_customer = len(allCustomers)
    total_product = ProductModel.objects.all()
    total_orders = Order.objects.all()
    completed_orders = Order.objects.filter(status='Completed')
    pending_order = []
    for i, j in zip(total_orders, completed_orders):
        if j == i:
            pass
        else:
            pending_order.append(i)
    total_shortages = ShortageOfProduct.objects.all()
    content = {
        'all_customers': allCustomers,
        'total_customer': total_customer,
        'total_product': total_product,
        'total_orders': total_orders,
        'total_shortage': total_shortages,
        'signupForm': form,
    }
    return render(request, 'App_main/Admin_dashboard.html', context=content)


@login_required
@user_passes_test(is_admin)
def admin_updates_asking_quantity(request):
    if request.method == 'POST':
        orderID = request.POST.get('orderID')
        quantity = request.POST.getlist('quantity')
        theOrders = Order.objects.get(id=orderID)
        for i, j in zip(theOrders.order_items.all(), quantity):
            j_int = int(j)
            if i.quantity < j_int:
                i.item.No_of_available -= (j_int - i.quantity)
            elif i.quantity > j_int:
                i.item.No_of_available += (i.quantity - j_int)
            i.item.save()
            i.quantity = j
            i.save()

        return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def update_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        product = ProductModel.objects.get(id=product_id)
        if price == "" and quantity == "":
            return HttpResponseRedirect(reverse('App_main:admin_dashboard'))
        elif price != "" and quantity != "":
            product.No_of_available += int(quantity)
            product.price_per_unit = int(price)
            product.save()
        elif quantity == "":
            product.price_per_unit = int(price)
            product.save()
        elif price == "":
            product.No_of_available += int(quantity)
            product.save()
    return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def delete_product(request, product_key):
    product = ProductModel.objects.get(id=product_key)
    product.delete()
    return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def delete_shortage_table(request, table_key):
    shortage_table = ShortageOfProduct.objects.get(id=table_key)
    shortage_table.delete()
    return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def register_user_by_admin(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            my_admin_group = Group.objects.get_or_create(name='CUSTOMER')
            my_admin_group[0].user_set.add(user)
            messages.info(request, "Successfully Registered")
            return HttpResponseRedirect(reverse('App_main:admin_dashboard'))
        else:
            messages.info(request, "Password doesn't match!!!")
            return redirect('App_main:admin_dashboard')


@login_required
@user_passes_test(is_admin)
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = request.POST.get("status_change")
        order.save()
        return HttpResponseRedirect(reverse('App_main:admin_dashboard'))


@login_required
@user_passes_test(is_admin)
def add_new_product(request):
    form = ProductModelForm()
    if request.method == 'POST':
        form = ProductModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('App_main:add-new-product'))

    content = {
        'form': form,
    }
    return render(request, 'App_main/add_new_product.html', context=content)


@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == 'POST':
        cat = request.POST.get('cat-name')
        category = CategoryModel(name=cat)
        category.save()
        return HttpResponseRedirect(reverse('App_main:add-new-product'))


@login_required
@user_passes_test(is_admin)
def admin_generates_invoice(request, OrderID):
    order = Order.objects.get(id=OrderID)
    total = list(range(1, len(order.order_items.all()) + 1))
    zip_item = zip(total, list(order.order_items.all()))
    content = {
        'order': order,
        'total_and_order': zip_item,
    }
    return render(request, 'App_main/invoice_page.html', context=content)


# <! ------- Super Admin Start ------->

@login_required
@user_passes_test(is_boss_admin)
def boss_admin_dashboard(request):
    form = SignUpForm()
    total_user = User.objects.filter(is_superuser=False)
    allCustomers = checkAdmin(list(total_user), [])
    total_customer = len(allCustomers)
    total_product = ProductModel.objects.all()
    total_orders = Order.objects.all()
    completed_orders = Order.objects.filter(status='Completed')
    pending_order = []
    for i, j in zip(total_orders, completed_orders):
        if j == i:
            pass
        else:
            pending_order.append(i)
    total_shortages = ShortageOfProduct.objects.all()
    content = {
        'all_customers': allCustomers,
        'total_customer': total_customer,
        'total_product': total_product,
        'total_orders': total_orders,
        'total_shortage': total_shortages,
        'signupForm': form,
    }
    return render(request, 'App_main/Boss_Admin_dashboard.html', context=content)


@login_required
@user_passes_test(is_boss_admin)
def boss_admin_updates_asking_quantity(request):
    if request.method == 'POST':
        orderID = request.POST.get('orderID')
        quantity = request.POST.getlist('quantity')
        theOrders = Order.objects.get(id=orderID)
        for i, j in zip(theOrders.order_items.all(), quantity):
            j_int = int(j)
            if i.quantity < j_int:
                i.item.No_of_available -= (j_int - i.quantity)
            elif i.quantity > j_int:
                i.item.No_of_available += (i.quantity - j_int)
            i.item.save()
            i.quantity = j
            i.save()

        return HttpResponseRedirect(reverse('App_main:boss-admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def boss_update_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        product = ProductModel.objects.get(id=product_id)
        if price == "" and quantity == "":
            return HttpResponseRedirect(reverse('App_main:boss-admin_dashboard'))
        elif price != "" and quantity != "":
            product.No_of_available += int(quantity)
            product.price_per_unit = int(price)
            product.save()
        elif quantity == "":
            product.price_per_unit = int(price)
            product.save()
        elif price == "":
            product.No_of_available += int(quantity)
            product.save()
    return HttpResponseRedirect(reverse('App_main:boss-admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def boss_delete_product(request, product_key):
    product = ProductModel.objects.get(id=product_key)
    product.delete()
    return HttpResponseRedirect(reverse('App_main:boss-admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def boss_delete_shortage_table(request, table_key):
    shortage_table = ShortageOfProduct.objects.get(id=table_key)
    shortage_table.delete()
    return HttpResponseRedirect(reverse('App_main:boss-admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def register_user_by_boss_admin(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                adminCheckbox = request.POST.get('admin-checkbox')
            except:
                adminCheckbox = None

            if adminCheckbox:
                my_admin_group = Group.objects.get_or_create(name='ADMIN')
                my_admin_group[0].user_set.add(user)
            else:
                my_admin_group = Group.objects.get_or_create(name='CUSTOMER')
                my_admin_group[0].user_set.add(user)
            messages.info(request, "Successfully Registered")
            return HttpResponseRedirect(reverse('App_main:boss_admin_dashboard'))
        else:
            messages.info(request, "Password doesn't match!!!")
            return redirect('App_main:boss-admin_dashboard')


@login_required
@user_passes_test(is_boss_admin)
def boss_update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        order.status = request.POST.get("status_change")
        order.save()
        return HttpResponseRedirect(reverse('App_main:boss-admin_dashboard'))


@login_required
@user_passes_test(is_boss_admin)
def boss_add_new_product(request):
    form = ProductModelForm()
    if request.method == 'POST':
        form = ProductModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('App_main:boss-add-new-product'))

    content = {
        'form': form,
    }
    return render(request, 'App_main/boss_add_new_product.html', context=content)


@login_required
@user_passes_test(is_boss_admin)
def boss_add_category(request):
    if request.method == 'POST':
        cat = request.POST.get('cat-name')
        category = CategoryModel(name=cat)
        category.save()
        return HttpResponseRedirect(reverse('App_main:boss-add-new-product'))


@login_required
@user_passes_test(is_boss_admin)
def boss_admin_generates_invoice(request, OrderID):
    order = Order.objects.get(id=OrderID)
    total = list(range(1, len(order.order_items.all()) + 1))
    zip_item = zip(total, list(order.order_items.all()))
    content = {
        'order': order,
        'total_and_order': zip_item,
    }
    return render(request, 'App_main/invoice_page.html', context=content)
