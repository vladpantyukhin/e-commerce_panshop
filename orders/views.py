from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render

from landing.forms import SubscriberForm

from .models import *
from .forms import CheckoutContactForm

def basket_adding(request):
    return_dict = dict()
    session_key = request.session.session_key
    print(request.POST)
    data = request.POST
    product_id = data.get("product_id")
    nmb = data.get("nmb")
    total_price = data.get("total_price")
    is_delete = data.get("is_delete")

    if is_delete == 'true' and nmb == '0':
        ProductInBasket.objects.filter(id=product_id).update(is_active=False)

    elif is_delete == 'true':
        ProductInBasket.objects.filter(id=product_id).update(nmb=nmb, total_price=total_price)
    else:
        new_product, created = ProductInBasket.objects.get_or_create(session_key=session_key, product_id=product_id, is_active=True, defaults={"nmb": nmb})
        if not created:
            new_product.nmb += int(nmb)
            new_product.save(force_update=True)

    products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True)
    products_total_nmb = products_in_basket.count()
    return_dict["products_total_nmb"] = products_total_nmb

    return_dict["products"] = list()
    for item in products_in_basket:
        product_dict = dict()
        product_dict["id"] = item.product.id
        product_dict["name"] = item.product.name
        product_dict["price_per_item"] = item.price_per_item
        product_dict["nmb"] = item.nmb
        return_dict["products"].append(product_dict)

    return JsonResponse(return_dict)

def checkout(request):
        session_key = request.session.session_key
        products_in_basket = ProductInBasket.objects.filter(session_key=session_key, is_active=True, order__isnull=True)
        print(products_in_basket)
        for item in products_in_basket:
            print(item.order)

        form = CheckoutContactForm(request.POST or None)
        if request.POST:
            print(request.POST)
            if form.is_valid():
                print("yes")
                data = request.POST
                name = data.get("name", "3423453")
                phone = data["phone"]
                comments = data.get("comments")
                user, created = User.objects.get_or_create(username=phone, defaults={"first_name": name})

                order = Order.objects.create(user=user, customer_name=name, customer_phone=phone, comments=comments, status_id=1)

                for name, value in data.items():
                    if name.startswith("product_in_basket_"):
                        product_in_basket_id = name.split("product_in_basket_")[1]
                        product_in_basket = ProductInBasket.objects.get(id=product_in_basket_id)
                        print(type(value))

                        product_in_basket.nmb = value
                        product_in_basket.order = order
                        product_in_basket.is_active = False
                        product_in_basket.save(force_update=True)

                        ProductInOrder.objects.create(product=product_in_basket.product, nmb=product_in_basket.nmb,
                                                      price_per_item=product_in_basket.price_per_item,
                                                      total_price=product_in_basket.total_price,
                                                      order=order)
                                                      
                        request.META['HTTP_REFERER'] = 'http://panshop.site/successful_order/'

                return HttpResponseRedirect(request.META['HTTP_REFERER'])
            else:
                print("no")

        return render(request, 'orders/checkout.html', locals())

def successful_order(request):

    form = SubscriberForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        print(request.POST)
        print(form.cleaned_data)
        data = form.cleaned_data
        print(data["name"])

        new_form = form.save()

    return render(request, 'orders/successful_order.html', locals())
