from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required

from .forms import RegisterUserForm
from .models import *


def login(request):
    return render(request, 'registration/login.html')


class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('login')


def validate_username(request):
    username = request.GET.get('username', None)
    response = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)


def about(request):
    return render(request, 'demo/about.html')


def contact(request):
    return render(request, 'demo/contact.html')


def product(request):
    return render(request, 'demo/product.html')


def catalog(request):
    products = Product.objects.filter(count__gte=1).order_by('-date')
    context = {
        'products': products,
    }
    return render(request, 'demo/catalog.html', context=context)


@login_required
def checkout(request):
    password = request.GET.get('password', None)
    valid = request.user.check_password(password)
    if not valid:
        return JsonResponse({
            'error': 'Неверный пароль'
        })
    item_in_cart = request.user.cart_set.all()
    if not item_in_cart:
        return JsonResponse({
            'error': 'Корзина пуста'
        })
    order = Order.objects.create(user=request.user)
    for item in item_in_cart:
        ItemInOrder.objects.create(order=order, product=item.product, count=item.count,
                                   price=item.product.price * item.count)

    item_in_cart.delete()
    return JsonResponse({
        'message': 'Заказ сделан    '
    })


@login_required
def cart(request):
    cart_item = request.user.cart_set.all().order_by('-id')
    context = {
        'cart_item': cart_item,
    }
    return render(request, 'demo/cart.html', context=context)


class OrderListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = "demo/orders.html"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-date')


@login_required
def delete_order(request, pk):
    order = Order.objects.filter(user=request.user, pk=pk)
    if order:
        order[0].status = 'canceled'
        order[0].save()
    return redirect('orders')


@login_required
def to_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    item_in_cart = Cart.objects.filter(user=request.user, product=item).first()
    if item_in_cart:
        if item.count == 0:
            return JsonResponse({
                'error': 'Can not add more'
            })

        item_in_cart.count += 1
        item_in_cart.save()
        item.count -= 1
        item.save()
        return JsonResponse({
            'count': item_in_cart.count
        }), redirect('cart')

    else:
        item_in_cart = Cart(user=request.user, product=item)
        item_in_cart.save()
        item.count -= 1
        item.save()
        return JsonResponse({
            'count': item_in_cart.count
        })


@login_required
def delete_cart(request, pk):
    item_cart = Cart.objects.get(user=request.user, pk=pk)
    item = item_cart.product
    if item_cart:
        item_cart.delete()
        item.count += item_cart.count
        item.save()

    return redirect('cart')


@login_required
def plus_cart(request, pk):
    item_cart = Cart.objects.get(user=request.user, pk=pk)
    item = item_cart.product
    if item_cart:
        if item.count <= 0:
            return redirect('cart')
        else:
            item_cart.count += 1
            item.count -= 1
            item_cart.save()
            item.save()

    return redirect('cart')


@login_required
def minus_cart(request, pk):
    item_cart = Cart.objects.get(user=request.user, pk=pk)
    item = item_cart.product
    if item_cart:
        if item_cart.count <= 0:
            return redirect('cart')
        else:
            item_cart.count -= 1
            item.count += 1
            item_cart.save()
            item.save()

            if item_cart.count == 0:
                delete_cart(request, pk)

    return redirect('cart')