import requests
from django.core.mail import EmailMultiAlternatives

from django.core.files.storage import FileSystemStorage
import json

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotAllowed

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

from rakubaru.models import Rmember, Route, Rpoint, Rpin, Paid, Device, Coupon, Area, Sublocality, AreaAssign, Product, Price
from rakubaru.serializers import RmemberSerializer, RouteSerializer, RpointSerializer, RpinSerializer, AreaSerializer, SublocalitySerializer, AreaAssignSerializer


import stripe

@csrf_exempt
def stripe_webhook_view(request):

    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY

    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        print('subscription deleted')
        members = Rmember.objects.filter(subscriptionID=subscription.id)
        if members.count() > 0:
            member = members.first()
            if member.subperiodend != '':
                now = int(round(time.time()))
                subscription_period_end = int(member.subperiodend)
                if now - subscription_period_end >= 86400 * 30:
                    member.subscriptionID = ''
                    member.subperiodend = ''
                    member.subscription_status = 'subscription_canceled'
                    member.save()
    elif event.type == 'invoice.payment_failed':
        invoice = event.data.object
        print('invoice payment failed')
        members = Rmember.objects.filter(customerID=invoice.customer)
        if members.count() > 0:
            member = members.first()
            print(member.customerID)
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)





































































