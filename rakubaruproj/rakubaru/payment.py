import requests
from django.core.mail import EmailMultiAlternatives

from django.core.files.storage import FileSystemStorage
import json

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotAllowed
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import time
from django.utils.datastructures import MultiValueDictKeyError
from django.db.models import Q

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from random import randint
from pyfcm import FCMNotification
import pyrebase
import stripe

from rakubaru.models import Rmember, Paid, Coupon, Product, Price, Invoice, Plan


def toplan(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    if me.plan == '':
        me.plan = '1'
        me.save()
    if me.planned_members == '':
        me.planned_members = '1'
        me.save()

    members = Rmember.objects.filter(admin_id=me.pk)
    count = members.count()
    ex_status = ''
    if count >= int(me.planned_members):
        ex_status = 'expired'

    if me.email != '':
        import datetime
        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
        # stripe_subscription_id = 'sub_JA6DSZQSjIJkVZ'
        invoiceList = []
        invoiceNumberList = []
        stripe_subscription_id = me.subscriptionID
        if stripe_subscription_id != '':
            invs = Invoice.objects.filter(member_id=me.pk)
            for inv in invs:
                invoiceList.insert(0,inv)
                invoiceNumberList.append(inv.number)
            invoices = stripe.Invoice.list(subscription=stripe_subscription_id)
            for inv in invoices:
                if not inv.number in invoiceNumberList:
                    invoice = Invoice()
                    invoice.member_id = me.pk
                    invoice.number = inv.number
                    invoice.receipt_number = inv.receipt_number
                    invoice.amount = inv.amount_paid
                    invoice.hosted_invoice_url = inv.hosted_invoice_url
                    invoice.invoice_pdf = inv.invoice_pdf
                    invoice.created_time = datetime.datetime.fromtimestamp(float(int(inv.created))).strftime("%m/%d/%Y %H:%m")
                    invoice.status = inv.status.capitalize()
                    invoiceList.append(invoice)

        plans = Plan.objects.all()

        if me.plan == '': me.plan = '1'

        context = {
            'me':me,
            'status':ex_status,
            'planned_count': int(me.planned_members),
            'memb_count': count,
            'invoices':invoiceList,
            'plans':plans,
        }

        return render(request, 'rakubaru/membership_plans.html', context)



@api_view(['GET', 'POST'])
def racreatesubscription(request):
    import datetime
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY

    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    if request.method == "POST":
        token = request.POST.get('token', '')
        price = request.POST.get('price', '')
        me_id = request.POST.get('me_id', '1')
        plan = request.POST.get('plan', '')
        membs = request.POST.get('members', '1')
        coupon_id = request.POST.get('coupon_id', '1')
        discount = request.POST.get('discount', '0')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        pay_method = request.POST.get('pay_method', '')

        amount = int(float(price))
        prices = Price.objects.filter(price=amount)
        priceID = ''
        products = Product.objects.all()
        product = None
        if products.count() > 0:
            product = products[0]
        else:
            product = create_product()
        if prices.count() > 0:
            prc = prices[0]
            priceID = prc.priceID
        else:
            prc = stripe.Price.create(
                nickname='Standard Monthly',
                product=product.productID,
                unit_amount=amount,
                currency='jpy',
                recurring={
                    'interval': 'month',
                    'usage_type': 'licensed',
                },
            )

            if prc is not None:
                priceID = prc.id
                prcs = Price.objects.filter(product_id=product.id, price=amount, priceID=prc.id)
                priceObj = None
                if prcs.count() == 0:
                    priceObj = Price()
                    priceObj.product_id = product.pk
                    priceObj.price = amount
                    priceObj.priceID = prc.id
                    priceObj.save()

        try:
            customer = stripe.Customer.create(name=name, email=email)
            if customer is not None:
                me.customerID = customer.id
                me.save()

            payment_method = stripe.PaymentMethod.attach(
                pay_method,
                customer=me.customerID,
            )
            if payment_method is not None:
                # Create the subscription
                subscription = stripe.Subscription.create(
                    default_payment_method=payment_method.id,
                    customer=me.customerID,
                    items=[{
                        'price': priceID
                    }],
                    expand=['latest_invoice.payment_intent'],
                )

                if subscription is not None:
                    me.planned_members = membs
                    me.plan = plan
                    me.subscriptionID = subscription.id
                    me.subperiodend = subscription.current_period_end
                    me.subscription_status = ''
                    me.pay_method = pay_method
                    me.payment_method_id = payment_method.id
                    me.save()

                    paid = Paid()
                    paid.member_id = me.pk
                    paid.plan = plan
                    paid.paid_time = str(int(round(time.time() * 1000)))
                    paid.coupon_id = coupon_id
                    paid.discount = discount
                    paid.discount_amount = str(int(amount * (100 / (100 - float(discount)) - 1)))
                    paid.paid_amount = str(amount)
                    paid.plan_members = membs
                    paid.save()

                    invoices = stripe.Invoice.list(subscription=subscription.id)
                    for inv in invoices:
                        invoice = Invoice()
                        invoice.member_id = me.pk
                        invoice.number = inv.number
                        invoice.receipt_number = inv.receipt_number
                        invoice.amount = inv.amount_paid
                        invoice.hosted_invoice_url = inv.hosted_invoice_url
                        invoice.invoice_pdf = inv.invoice_pdf
                        invoice.created_time = datetime.datetime.fromtimestamp(float(int(inv.created))).strftime("%m/%d/%Y %H:%m")
                        invoice.status = inv.status.capitalize()
                        invoice.save()

                    return HttpResponse('success')

                else:
                    return HttpResponse('支払いエラー。')

        except stripe.error.InvalidRequestError as e:
            return HttpResponse(str(e))


@api_view(['GET', 'POST'])
def rachangesubscription(request):
    import datetime
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY

    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    if request.method == "POST":
        price = request.POST.get('price', '')
        me_id = request.POST.get('me_id', '1')
        plan = request.POST.get('plan', '')
        membs = request.POST.get('members', '1')
        coupon_id = request.POST.get('coupon_id', '1')
        discount = request.POST.get('discount', '0')

        amount = int(float(price))
        prices = Price.objects.filter(price=amount)
        priceID = ''
        products = Product.objects.all()
        product = None
        if products.count() > 0:
            product = products[0]
        else:
            product = create_product()
        if prices.count() > 0:
            prc = prices[0]
            priceID = prc.priceID
        else:
            prc = stripe.Price.create(
                nickname='Standard Monthly',
                product=product.productID,
                unit_amount=amount,
                currency='jpy',
                recurring={
                    'interval': 'month',
                    'usage_type': 'licensed',
                },
            )

            if prc is not None:
                priceID = prc.id
                prcs = Price.objects.filter(product_id=product.id, price=amount, priceID=prc.id)
                priceObj = None
                if prcs.count() == 0:
                    priceObj = Price()
                    priceObj.product_id = product.pk
                    priceObj.price = amount
                    priceObj.priceID = prc.id
                    priceObj.save()

        if me.subscriptionID != '':
            try:
                stripe.Subscription.delete(me.subscriptionID, invoice_now=True, prorate=True)

                subscription = stripe.Subscription.create(
                    default_payment_method=me.payment_method_id,
                    customer=me.customerID,
                    items=[{
                        'price': priceID
                    }],
                    expand=['latest_invoice.payment_intent'],
                )

                # return HttpResponse('subscription: ' + str(subscription.id))

                if subscription is not None:
                    me.planned_members = membs
                    me.plan = plan
                    me.subscriptionID = subscription.id
                    me.subperiodend = subscription.current_period_end
                    me.subscription_status = ''
                    me.save()

                    paid = Paid()
                    paid.member_id = me.pk
                    paid.plan = plan
                    paid.paid_time = str(int(round(time.time() * 1000)))

                    paid.coupon_id = coupon_id
                    paid.discount = discount
                    paid.discount_amount = str(int(amount * (100 / (100 - float(discount)) - 1)))

                    paid.paid_amount = str(amount)
                    paid.plan_members = membs
                    paid.save()

                    invoices = stripe.Invoice.list(subscription=subscription.id)
                    for inv in invoices:
                        invoice = Invoice()
                        invoice.member_id = me.pk
                        invoice.number = inv.number
                        invoice.receipt_number = inv.receipt_number
                        invoice.amount = inv.amount_paid
                        invoice.hosted_invoice_url = inv.hosted_invoice_url
                        invoice.invoice_pdf = inv.invoice_pdf
                        invoice.created_time = datetime.datetime.fromtimestamp(float(int(inv.created))).strftime("%m/%d/%Y %H:%m")
                        invoice.status = inv.status.capitalize()
                        invoice.save()

                    return HttpResponse('success')

                else:
                    return HttpResponse('支払いエラー。')

            except stripe.error.InvalidRequestError as e:
                return HttpResponse(str(e))

        else:
            return HttpResponse('サブスクリプションはありません。')



def rasubscriptiondelete(request):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    members = Rmember.objects.filter(admin_id=me.pk)
    if members.count() > 1:
        return HttpResponse('1')

    if me.subscriptionID != '':
        stripe.Subscription.delete(me.subscriptionID, invoice_now=True, prorate=True)

    me.planned_members = '1'
    me.plan = '1'
    me.subscriptionID = ''
    me.subperiodend = ''
    me.subscription_status = ''
    me.save()

    paid = Paid()
    paid.member_id = me.pk
    paid.plan = '1'
    paid.paid_time = str(int(round(time.time() * 1000)))
    paid.coupon_id = '0'
    paid.discount = '0'
    paid.discount_amount = '0'
    paid.paid_amount = '0'
    paid.plan_members = '1'
    paid.save()

    return HttpResponse('0')




def createproduct(request):
    product = create_product()
    if product is not None:
        return HttpResponse('New product has been created!')
    else:
        return HttpResponse('New product creation failed')


def create_product():
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY

    product = stripe.Product.create(
      name='Rakubaru Membership',
      type='service',
    )

    if product is not None :
        prods = Product.objects.filter(productID=product.id)
        prod = None
        if prods.count() == 0:
            prod = Product()
            prod.name = 'Rakubaru Membership'
            prod.type = 'service'
            prod.productID = product.id
            prod.save()
        else:
            prod = products[0]

        price = stripe.Price.create(
            nickname='Standard Monthly',
            product=product.id,
            unit_amount=5000,
            currency='jpy',
            recurring={
                'interval': 'month',
                'usage_type': 'licensed',
            },
        )

        if price is not None:
            prcs = Price.objects.filter(product_id=prod.id, price=5000, priceID=price.id)
            prc = None
            if prcs.count() == 0:
                prc = Price()
                prc.product_id = prod.pk
                prc.price = 5000
                prc.priceID = price.id
                prc.save()

                return prod

    return None



def getmysubscriptions(request):
    import datetime
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    stripe_subscription_id = 'sub_JXi73jbg9HPXpU'
    invoices = stripe.Invoice.list(subscription=stripe_subscription_id)
    invoiceList = []
    for inv in invoices:
        data = {
            'number':inv.number,
            'receipt_number':inv.receipt_number,
            'status':inv.status.capitalize(),
            'created':datetime.datetime.fromtimestamp(float(int(inv.created))).strftime("%d %b, %Y"),
            'amount':inv.amount_paid,
            'hosted_invoice_url':inv.hosted_invoice_url,
            'invoice_pdf':inv.invoice_pdf,
        }
        invoiceList.append(data)
    return HttpResponse(json.dumps(invoiceList))



@api_view(['GET', 'POST'])
def rachecksubscription(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    if me.email == 'yamamoto_h@nac-om.com':
        return HttpResponse('0')

    members = Rmember.objects.filter(admin_id=me.pk)
    if me.planned_members == '':
        me.planned_members = '1'
        me.save()
    count = members.count()
    if count >= int(me.planned_members):
        return HttpResponse('1')
    else:
        return HttpResponse('0')



















































































































