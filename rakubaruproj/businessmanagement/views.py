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

from rakubaru.models import Rmember, CompanyInfo, CustomerInfo, ProductInfo, DistributionAreaInfo, DistributionAreaGroupInfo, DistributionAreaGroup, DistributorInfo, LeaderInfo, DistributorGroupInfo, SubcontractorInfo
from rakubaru.models import IndustryInfo, DistributionTypeInfo
from rakubaru.serializers import RmemberSerializer, CompanyInfoSerializer, CustomerInfoSerializer, ProductInfoSerializer, DistributionAreaInfoSerializer, DistributionAreaGroupInfoSerializer, DistributorInfoSerializer
from rakubaru.serializers import LeaderInfoSerializer, DistributorGroupInfoSerializer, SubcontractorInfoSerializer, IndustryInfoSerializer

def now():
    from datetime import datetime
    return datetime.now()


def index(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']
    members = Rmember.objects.filter(id=myID)
    if members.count() > 0:
        me = members.first()
        return render(request, 'businessmanagement/home.html', {'me':me})
    notice = ''
    try: notice = request.GET['notice']
    except KeyError: print('No notice')
    return render(request, 'businessmanagement/login.html', {'notice':notice})


@api_view(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        members = Rmember.objects.filter(email=email, password=password)
        if members.count() > 0:
            member = members.first()
            request.session['bID'] = member.pk
            return redirect('/businessmanagement/')
        else:
            return respond('Eメールまたはパスワードが間違っています。')


def respond(message):
    return redirect('/businessmanagement/response?message=' + message)


def response(request):
    message = request.GET['message']
    return render(request, 'businessmanagement/response.html', {'message': message})


def logout(request):
    request.session['bID'] = ''
    return redirect('/businessmanagement/')


def company_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    infos = CompanyInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'companyinfos':infos,
        'page':'company_master'
    }
    return render(request, 'businessmanagement/company_master.html', context)


@api_view(['POST','GET'])
def company_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        company_name = request.POST.get('company_name', '')
        manager = request.POST.get('manager', '')
        phone_number = request.POST.get('phone_number', '')
        fax_number = request.POST.get('fax_number', '')
        email = request.POST.get('email', '')
        postal_code = request.POST.get('postal_code', '')
        address = request.POST.get('address', '')
        bank_name = request.POST.get('bank_name', '')
        branch_name = request.POST.get('branch_name', '')
        account_type = request.POST.get('account_type', '')
        account_number = request.POST.get('account_number', '')
        invoice_issuer_number = request.POST.get('invoice_issuer_number', '')
        invoice_number = request.POST.get('invoice_number', '')
        note = request.POST.get('note', '')

        info = None
        infos = CompanyInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            info = CompanyInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.company_name = company_name
        info.manager = manager
        info.phone_number = phone_number
        info.fax_number = fax_number
        info.email = email
        info.postal_code = postal_code
        info.address = address
        info.bank_name = bank_name
        info.branch_name = branch_name
        info.account_type = account_type
        info.account_number = account_number
        info.invoice_issuer_number = invoice_issuer_number
        info.invoice_number = invoice_number
        info.note = note
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/company-master')



def delete_company_info(request):
    info_id = request.GET['info_id']
    CompanyInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/company-master')


def customer_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    industryinfos = IndustryInfo.objects.filter(member_id=myID)

    infos = CustomerInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'customerinfos':infos,
        'page':'customer_master',
        'industryinfos':industryinfos
    }
    return render(request, 'businessmanagement/customer_master.html', context)



@api_view(['POST','GET'])
def customer_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        customer_name = request.POST.get('customer_name', '')
        industry = request.POST.get('industry', '')
        note = request.POST.get('note', '')
        phone_number = request.POST.get('phone_number', '')
        fax_number = request.POST.get('fax_number', '')
        email = request.POST.get('email', '')
        postal_code = request.POST.get('postal_code', '')
        address = request.POST.get('address', '')
        url = request.POST.get('url', '')
        report_password = request.POST.get('report_password', '')

        info = None
        infos = CustomerInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = CustomerInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = CustomerInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.customer_name = customer_name
        info.industry = industry
        info.note = note
        info.phone_number = phone_number
        info.fax_number = fax_number
        info.emails = email
        info.postal_code = postal_code
        info.address = address
        info.url = url
        info.report_password = report_password
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/customer-master')



def delete_customer_info(request):
    info_id = request.GET['info_id']
    CustomerInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/customer-master')



def product_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    infos = ProductInfo.objects.filter(member_id=myID).order_by('-id')
    cusinfos = CustomerInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'productinfos':infos,
        'page':'product_master',
        'customerinfos':cusinfos,
    }
    return render(request, 'businessmanagement/product_master.html', context)



@api_view(['POST','GET'])
def product_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        product_name = request.POST.get('product_name', '')
        contract_unit_price = request.POST.get('contract_unit_price', '')
        payment_unit_price_all = request.POST.get('payment_unit_price_all', '')
        payment_unit_price_eaves = request.POST.get('payment_unit_price_eaves', '')
        payment_unit_price_set = request.POST.get('payment_unit_price_set', '')
        payment_unit_price_detached = request.POST.get('payment_unit_price_detached', '')
        customers = request.POST.get('customers', '')
        note = request.POST.get('note', '')
        leader_work_unit_price = request.POST.get('leader_work_unit_price', '')

        info = None
        infos = ProductInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = ProductInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = ProductInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.product_name = product_name
        info.contract_unit_price = contract_unit_price
        info.payment_unit_price_all = payment_unit_price_all
        info.payment_unit_price_eaves = payment_unit_price_eaves
        info.payment_unit_price_set = payment_unit_price_set
        info.payment_unit_price_detached = payment_unit_price_detached
        info.customers = customers
        info.note = note
        info.leader_work_unit_price = leader_work_unit_price
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/product-master')



def delete_product_info(request):
    info_id = request.GET['info_id']
    ProductInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/product-master')



def distribution_area_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    infos = DistributionAreaInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'distributionareainfos':infos,
        'page':'distribution_area_master',
    }
    return render(request, 'businessmanagement/distribution_area_master.html', context)



@api_view(['POST','GET'])
def distribution_area_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        area_name = request.POST.get('area_name', '')
        copies = request.POST.get('copies', '0')
        payment_unit_price_all = request.POST.get('payment_unit_price_all', '')
        payment_unit_price_eaves = request.POST.get('payment_unit_price_eaves', '')
        payment_unit_price_set = request.POST.get('payment_unit_price_set', '')
        payment_unit_price_detached = request.POST.get('payment_unit_price_detached', '')
        allowance_all = request.POST.get('allowance_all', '')
        allowance_eaves = request.POST.get('allowance_eaves', '')
        allowance_set = request.POST.get('allowance_set', '')
        allowance_detached = request.POST.get('allowance_detached', '')
        amount_all = request.POST.get('amount_all', '')
        amount_eaves = request.POST.get('amount_eaves', '')
        amount_set = request.POST.get('amount_set', '')
        amount_detached = request.POST.get('amount_detached', '')
        distance_all = request.POST.get('distance_all', '')
        distance_eaves = request.POST.get('distance_eaves', '')
        distance_set = request.POST.get('distance_set', '')
        distance_detached = request.POST.get('distance_detached', '')
        note = request.POST.get('note', '')

        info = None
        infos = DistributionAreaInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = DistributionAreaInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = DistributionAreaInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.area_name = area_name
        info.copies = copies
        info.payment_unit_price_all = payment_unit_price_all
        info.payment_unit_price_eaves = payment_unit_price_eaves
        info.payment_unit_price_set = payment_unit_price_set
        info.payment_unit_price_detached = payment_unit_price_detached
        info.allowance_all = allowance_all
        info.allowance_eaves = allowance_eaves
        info.allowance_set = allowance_set
        info.allowance_detached = allowance_detached
        info.amount_all = amount_all
        info.amount_eaves = amount_eaves
        info.amount_set = amount_set
        info.amount_detached = amount_detached
        info.distance_all = distance_all
        info.distance_eaves = distance_eaves
        info.distance_set = distance_set
        info.distance_detached = distance_detached
        info.note = note
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/distribution-area-master')



def delete_distribution_area_info(request):
    info_id = request.GET['info_id']
    DistributionAreaInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/distribution-area-master')



def distribution_area_group_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    allareainfos = DistributionAreaInfo.objects.filter(member_id=myID)

    infos = DistributionAreaGroupInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'distributionareagroupinfos':infos,
        'page':'distribution_area_group_master',
        'allareainfos': allareainfos,
    }
    return render(request, 'businessmanagement/distribution_area__group_master.html', context)



@api_view(['POST','GET'])
def distribution_area_group_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        area_group_name = request.POST.get('area_group_name', '')
        areas = request.POST.get('areas', '')
        note = request.POST.get('note', '')

        info = None
        infos = DistributionAreaGroupInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = DistributionAreaGroupInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = DistributionAreaGroupInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.area_group_name = area_group_name
        info.areas = areas
        info.note = note
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/distribution-area-group-master')



def delete_distribution_area_group_info(request):
    info_id = request.GET['info_id']
    DistributionAreaGroupInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/distribution-area-group-master')




def distributor_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    allareainfos = DistributionAreaInfo.objects.filter(member_id=myID)

    infos = DistributorInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'distributorinfos':infos,
        'page':'distributor_master',
        'allareainfos': allareainfos,
    }
    return render(request, 'businessmanagement/distributor_master.html', context)




@api_view(['POST','GET'])
def distributor_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email', '')
        postal_code = request.POST.get('postal_code', '')
        address = request.POST.get('address', '')
        bank_name = request.POST.get('bank_name', '')
        branch_name = request.POST.get('branch_name', '')
        account_type = request.POST.get('account_type', '')
        account_number = request.POST.get('account_number', '')
        invoice_issuer_number = request.POST.get('invoice_issuer_number', '')
        invoice_number = request.POST.get('invoice_number', '')
        areas = request.POST.get('areas', '')
        is_leader = request.POST.get('is_leader', '')
        note = request.POST.get('note', '')

        info = None
        infos = DistributorInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = DistributorInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = DistributorInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.name = name
        info.phone_number = phone_number
        info.email = email
        info.postal_code = postal_code
        info.address = address
        info.bank_name = bank_name
        info.branch_name = branch_name
        info.account_type = account_type
        info.account_number = account_number
        info.invoice_issuer_number = invoice_issuer_number
        info.invoice_number = invoice_number
        info.areas = areas
        info.is_leader = is_leader
        info.note = note
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/distributor-master')



def delete_distributor_info(request):
    info_id = request.GET['info_id']
    DistributorInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/distributor-master')



def leader_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    allareainfos = DistributionAreaInfo.objects.filter(member_id=myID)

    infos = LeaderInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'leaderinfos':infos,
        'page':'leader_master',
        'allareainfos': allareainfos,
    }
    return render(request, 'businessmanagement/leader_master.html', context)




@api_view(['POST','GET'])
def leader_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        name = request.POST.get('name', '')
        areas = request.POST.get('areas', '')
        note = request.POST.get('note', '')

        info = None
        infos = LeaderInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = LeaderInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = LeaderInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.name = name
        info.areas = areas
        info.note = note
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/leader-master')



def delete_leader_info(request):
    info_id = request.GET['info_id']
    LeaderInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/leader-master')



def distributor_group_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    distributorinfos = DistributorInfo.objects.filter(member_id=myID)

    infos = DistributorGroupInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'distributorgroupinfos':infos,
        'page':'distributor_group_master',
        'distributorinfos': distributorinfos,
    }
    return render(request, 'businessmanagement/distributor_group_master.html', context)




@api_view(['POST','GET'])
def distributor_group_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        group_name = request.POST.get('group_name', '')
        distributors = request.POST.get('distributors', '')
        note = request.POST.get('note', '')

        info = None
        infos = DistributorGroupInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = DistributorGroupInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = DistributorGroupInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.group_name = group_name
        info.distributors = distributors
        info.note = note
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/distributor-group-master')



def delete_distributor_group_info(request):
    info_id = request.GET['info_id']
    DistributorGroupInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/distributor-group-master')




def subcontractor_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    allareainfos = DistributionAreaInfo.objects.filter(member_id=myID)
    industryinfos = IndustryInfo.objects.filter(member_id=myID)

    infos = SubcontractorInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'subcontractorinfos':infos,
        'page':'subcontractor_master',
        'allareainfos': allareainfos,
        'industryinfos':industryinfos
    }
    return render(request, 'businessmanagement/subcontractor_master.html', context)



@api_view(['POST','GET'])
def subcontractor_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        company_name = request.POST.get('company_name', '')
        industry = request.POST.get('industry', '')
        note = request.POST.get('note', '')
        phone_number = request.POST.get('phone_number', '')
        fax_number = request.POST.get('fax_number', '')
        email = request.POST.get('email', '')
        postal_code = request.POST.get('postal_code', '')
        address = request.POST.get('address', '')
        url = request.POST.get('url', '')
        areas = request.POST.get('areas', '')

        info = None
        infos = SubcontractorInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = SubcontractorInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = SubcontractorInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.company_name = company_name
        info.industry = industry
        info.note = note
        info.phone_number = phone_number
        info.fax_number = fax_number
        info.emails = email
        info.postal_code = postal_code
        info.address = address
        info.url = url
        info.areas = areas
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/subcontractor-master')



def delete_subcontractor_info(request):
    info_id = request.GET['info_id']
    SubcontractorInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/subcontractor-master')



def industry_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    infos = IndustryInfo.objects.filter(member_id=myID).order_by('-id')
    context = {
        'industryinfos':infos,
        'page':'other_industry_master',
    }
    return render(request, 'businessmanagement/other_industry_master.html', context)




@api_view(['POST','GET'])
def industry_register(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    if request.method == 'POST':
        info_id = request.POST.get('info_id', '0')
        code = request.POST.get('code', '')
        industry_name = request.POST.get('industry_name', '')
        note = request.POST.get('note', '')

        info = None
        infos = IndustryInfo.objects.filter(id=info_id)
        if infos.count() == 0:
            infos = IndustryInfo.objects.filter(code=code)
            if infos.count() > 0: return respond('コードはすでに存在します。 別のコードで再試行してください。')
            info = IndustryInfo()
        else:
            info = infos.first()
        info.member_id = myID
        info.code = code
        info.industry_name = industry_name
        info.note = note
        if info.created_on == '': info.created_on = now().strftime("%Y-%m-%d-%H-%M-%S")
        info.save()

    return redirect('/businessmanagement/other-industry-master')



def delete_industry_info(request):
    info_id = request.GET['info_id']
    IndustryInfo.objects.filter(id=info_id).delete()
    return redirect('/businessmanagement/other-industry-master')



def distribution_type_master(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    infos = DistributionTypeInfo.objects.filter(member_id=myID).order_by('-id')
    info = None
    if infos.count() > 0: info = infos.first()
    context = {
        'info':info,
        'page':'other_distribution_type_master',
    }
    return render(request, 'businessmanagement/other_distribution_type_master.html', context)




def distribution_type_save(request):
    try:
        if request.session['bID'] == 0 or request.session['bID'] == '':
            return render(request, 'businessmanagement/login.html')
    except KeyError:
        print('no session')
        return render(request, 'businessmanagement/login.html')
    myID = request.session['bID']

    type = request.GET['type']
    val = request.GET['val']

    dtypeinfos = DistributionTypeInfo.objects.filter(member_id=myID)
    dtypeinfo = None
    if dtypeinfos.count() == 0:
        dtypeinfo = DistributionTypeInfo()
    else:
        dtypeinfo = dtypeinfos.first()
    dtypeinfo.member_id = myID
    if type == 'all': dtypeinfo.all = val
    if type == 'eaves': dtypeinfo.eaves = val
    if type == 'set': dtypeinfo.set = val
    if type == 'detached': dtypeinfo.detached = val
    dtypeinfo.save()

    return redirect('/businessmanagement/other-distribution-type-master')






































































