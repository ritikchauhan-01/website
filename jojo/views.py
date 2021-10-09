from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from . models import *
from . utils import cookieCart ,cartData, guestOrder

# Create your views here.
def home(request):
    context = {}

    return render(request,'jojo/home.html',context)

# def store(request):
#     context = {}

#     return render(request,'jojo/store.html',context)

def about(request):
    context ={}

    return render(request,'jojo/about.html',context)

def faq(request):
    context = {}

    return render(request,'jojo/faq.html',context)

def contact(request):
    context = {}

    return render(request,'jojo/contact_us.html',context)

def store(request):
    
    Data = cartData(request)
    cartItems = Data['cartItems']
    items = Data['items']
    order = Data['order']


    products =Product.objects.all()
    context = {'products':products,'cartItems':cartItems}
    return render(request,'jojo/store.html',context)

def cart(request):

    Data = cartData(request)
    cartItems = Data['cartItems']
    items = Data['items']
    order = Data['order']

    context = {'items':items,'order':order,'cartItems':cartItems,'shipping':False}
    return render(request,'jojo/cart.html',context)

def checkout(request):

    Data = cartData(request)
    cartItems = Data['cartItems']
    items = Data['items']
    order = Data['order']
        
    context = {'items':items, 'order':order,'cartItems':cartItems}
    return render(request,'jojo/checkout.html',context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('action:',action)
    print('productId:',productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)

    orderItem,created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)

    else:
        customer, order = guestOrder(request, data)


    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
        customer = customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
    )

    return JsonResponse('Pament complete',safe=False)