import sys
import requests
from django.db import models
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

from rakubaru.models import ZPref1, ZPref01, ZPref2, ZPref3, ZPref4, ZPref5, ZPref6, ZPref7, ZPref8, ZPref9, ZPref10, ZPref11, ZPref12, ZPref13, ZPref14, ZPref15, ZPref16, ZPref17, ZPref18, ZPref19, ZPref20
from rakubaru.models import ZPref21, ZPref22, ZPref23, ZPref24, ZPref25, ZPref26, ZPref27, ZPref28, ZPref29, ZPref30, ZPref31, ZPref32, ZPref33, ZPref34, ZPref35, ZPref36, ZPref37, ZPref38, ZPref39, ZPref40
from rakubaru.models import ZPref41, ZPref42, ZPref43, ZPref44, ZPref45, ZPref46, ZPref47

prefs = {
    # '北海道':ZPref1,
    '北海道':ZPref01,
    '青森県':ZPref2,
    '岩手県':ZPref3,
    '宮城県':ZPref4,
    '秋田県':ZPref5,
    '山形県':ZPref6,
    '福島県':ZPref7,
    '茨城県':ZPref8,
    '栃木県':ZPref9,
    '群馬県':ZPref10,
    '埼玉県':ZPref11,
    '千葉県':ZPref12,
    '東京都':ZPref13,
    '神奈川県':ZPref14,
    '新潟県':ZPref15,
    '富山県':ZPref16,
    '石川県':ZPref17,
    '福井県':ZPref18,
    '山梨県':ZPref19,
    '長野県':ZPref20,
    '岐阜県':ZPref21,
    '静岡県':ZPref22,
    '愛知県':ZPref23,
    '三重県':ZPref24,
    '滋賀県':ZPref25,
    '京都府':ZPref26,
    '大阪府':ZPref27,
    '兵庫県':ZPref28,
    '奈良県':ZPref29,
    '和歌山県':ZPref30,
    '鳥取県':ZPref31,
    '島根県':ZPref32,
    '岡山県':ZPref33,
    '広島県':ZPref34,
    '山口県':ZPref35,
    '徳島県':ZPref36,
    '香川県':ZPref37,
    '愛媛県':ZPref38,
    '高知県':ZPref39,
    '福岡県':ZPref40,
    '佐賀県':ZPref41,
    '長崎県':ZPref42,
    '熊本県':ZPref43,
    '大分県':ZPref44,
    '宮崎県':ZPref45,
    '鹿児島県':ZPref46,
    '沖縄県':ZPref47,
}

en_prefs = {
    # 'Hokkaido':ZPref1,
    'Hokkaido':ZPref01,
    'Aomori':ZPref2,
    'Iwate':ZPref3,
    'Miyagi':ZPref4,
    'Akita':ZPref5,
    'Yamagata':ZPref6,
    'Fukushima':ZPref7,
    'Ibaraki':ZPref8,
    'Tochigi':ZPref9,
    'Gunma':ZPref10,
    'Saitama':ZPref11,
    'Chiba':ZPref12,
    'Tokyo':ZPref13,
    'Kanagawa':ZPref14,
    'Niigata':ZPref15,
    'Toyama':ZPref16,
    'Ishikawa':ZPref17,
    'Fukui':ZPref18,
    'Yamanashi':ZPref19,
    'Nagano':ZPref20,
    'Gifu':ZPref21,
    'Shizuoka':ZPref22,
    'Aichi':ZPref23,
    'Mie':ZPref24,
    'Shiga':ZPref25,
    'Kyoto':ZPref26,
    'Osaka':ZPref27,
    'Hyogo':ZPref28,
    'Nara':ZPref29,
    'Wakayama':ZPref30,
    'Tottori':ZPref31,
    'Shimane':ZPref32,
    'Okayama':ZPref33,
    'Hiroshima':ZPref34,
    'Yamaguchi':ZPref35,
    'Tokushima':ZPref36,
    'Kagawa':ZPref37,
    'Ehime':ZPref38,
    'Kochi':ZPref39,
    'Fukuoka':ZPref40,
    'Saga':ZPref41,
    'Nagasaki':ZPref42,
    'Kumamoto':ZPref43,
    'Oita':ZPref44,
    'Miyazaki':ZPref45,
    'Kagoshima':ZPref46,
    'Okinawa':ZPref47,
}


prefectures = [None, ZPref1, ZPref01, ZPref2, ZPref3, ZPref4, ZPref5, ZPref6, ZPref7, ZPref8, ZPref9, ZPref10, ZPref11, ZPref12, ZPref13, ZPref14, ZPref15, ZPref16, ZPref17, ZPref18, ZPref19, ZPref20,
              ZPref21, ZPref22, ZPref23, ZPref24, ZPref25, ZPref26, ZPref27, ZPref28, ZPref29, ZPref30, ZPref31, ZPref32, ZPref33, ZPref34, ZPref35, ZPref36, ZPref37, ZPref38, ZPref39, ZPref40,
              ZPref41, ZPref42, ZPref43, ZPref44, ZPref45, ZPref46, ZPref47,
            ]


def regregion(request):

    fs = FileSystemStorage()

    file = fs.open('1_Hokkaido.json')
    points = ''

    for line in file:
        decoded_line = line.decode("utf-8")
        points = points + decoded_line

    if points != '':
        points = points.replace('\\','')
        try:
            decoded = json.loads(points)

            regions = decoded['features']

            for region in regions:
                coords = region['geometry']['coordinates']
                pref_name = region['properties']['PREF_NAME']
                city_name = region['properties']['CITY_NAME']
                s_name = region['properties']['S_NAME']

                regions = ZPref01.objects.filter(PREF_NAME=pref_name, CITY_NAME=city_name, S_NAME=s_name)
                if regions.count() > 0:
                    continue
                region = ZPref01()
                region.PREF_NAME = pref_name
                region.CITY_NAME = city_name
                region.S_NAME = s_name
                region.COORDS_JSON = coords
                region.save()

            return HttpResponse('Success!' + '///' + file.name)

        except Exception as e:
            print(get_full_class_name(e))
            return HttpResponse(get_full_class_name(e))

    return HttpResponse('Error!')


def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__



def delregion(request):
    regions = ZPref1.objects.filter(PREF_NAME='福岡県')
    regions.delete()
    return HttpResponse('Deletion is success')


def dispregion(request):
    # fs = FileSystemStorage()

    # file = fs.open('1_Hokkaido.json')
    # points = ''

    # for line in file:
    #     decoded_line = line.decode("utf-8")
    #     points = points + decoded_line

    # if points != '':
    #     points = points.replace('\\','')
    #     try:
    #         decoded = json.loads(points)

    #         regions = decoded['features']

    #         return HttpResponse(len(regions))

    #     except Exception as e:
    #         print(get_full_class_name(e))
    #         return HttpResponse(get_full_class_name(e))

    # return HttpResponse('0')

    regions = ZPref01.objects.all()
    return HttpResponse(regions.count())


def modeltest(request):
    regions = prefs['region'].objects.all()
    return HttpResponse(regions.count())


from html.parser import HTMLParser

def findregions(request):
    pref = request.GET['pref']
    city = request.GET['city']
    sname = request.GET['sname']

    sname = sname.replace('0','０').replace('1','１').replace('2','２').replace('3','３').replace('4','４').replace('5','５').replace('6','６').replace('7','７').replace('8','８').replace('9','９')


    # pref = HTMLParser().unescape( pref )
    # city = HTMLParser().unescape( city )
    # sname = HTMLParser().unescape( sname )

    # pref = '福岡県'
    # city = '門司区'
    # sname = '青葉台'

    regionList = []
    if not prefs[pref] is None:
        regions = []
        if sname == '':
            regions = prefs[pref].objects.filter(CITY_NAME=city)
        else:
            regions = prefs[pref].objects.filter(CITY_NAME=city, S_NAME=sname)
        for region in regions:
            data = {
                'pref_name': region.PREF_NAME,
                'city_name': region.CITY_NAME,
                's_name': region.S_NAME,
                'coordinates': json.loads(region.COORDS_JSON)
            }
            regionList.append(data)

    return HttpResponse(json.dumps(regionList))


























































