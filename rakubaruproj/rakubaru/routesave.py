from django.test import TestCase

import requests
from django.core.mail import EmailMultiAlternatives

from django.core.files.storage import FileSystemStorage
import json
import os

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

from rakubaru.models import Rmember, Route, Rpoint, Rpin, Paid, Device, Coupon, Area, Sublocality, AreaAssign, Product, Price, Invoice, Plan, PointJsonData, PointData
from rakubaru.serializers import RmemberSerializer, RouteSerializer, RpointSerializer, RpinSerializer, AreaSerializer, SublocalitySerializer, AreaAssignSerializer



@api_view(['GET', 'POST'])
def startreporting(request):
    if request.method == 'POST':
        route_id = request.POST.get('route_id', '0')
        member_id = request.POST.get('member_id', '0')
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        start_time = request.POST.get('start_time', '0')
        end_time = request.POST.get('end_time', '0')
        duration = request.POST.get('duration', '0')
        speed = request.POST.get('speed', '0')
        distance = request.POST.get('distance', '0')

        if int(duration) > 0 and int(route_id) == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        route = Route()
        route.admin_id = member.admin_id
        route.member_id = member_id
        try:
            assign_id = request.POST.get('assign_id', '0')
            route.assign_id = assign_id
        except KeyError:
            print('no key')
            route.assign_id = '0'
        if name != '':
            route.name = name
        route.description = description
        route.admin_desc = description
        route.start_time = start_time
        route.end_time = end_time
        route.duration = duration
        route.speed = speed
        route.distance = distance
        route.reported_time = str(int(round(time.time() * 1000)))
        route.status = 'reported'
        route.save()

        folder = settings.MEDIA_ROOT + '/points/'

        fs = FileSystemStorage(location=folder)

        lat = request.POST.get('lat', '0')
        lng = request.POST.get('lng', '0')
        comment = request.POST.get('comment', '')
        color = request.POST.get('color', '')
        tm = request.POST.get('tm', '')

        pnt = Rpoint()
        pnt.id = 1
        pnt.route_id = route.pk
        pnt.lat = lat
        pnt.lng = lng
        pnt.comment = comment
        pnt.color = color
        pnt.time = tm

        pointList = []
        pointList.append(pnt)

        file_path = 'route_' + str(route.pk) + '.json'

        data = {
            'points':RpointSerializer(pointList, many=True).data
        }

        f = fs.open(file_path, 'w+')
        f.write(json.dumps(data))

        resp = {'result_code': '0', 'route_id': str(route.pk)}
        return HttpResponse(json.dumps(resp))




@api_view(['GET', 'POST'])
def endreporting(request):
    if request.method == 'POST':
        route_id = request.POST.get('route_id', '0')
        member_id = request.POST.get('member_id', '0')
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        start_time = request.POST.get('start_time', '0')
        end_time = request.POST.get('end_time', '0')
        duration = request.POST.get('duration', '0')
        speed = request.POST.get('speed', '0')
        distance = request.POST.get('distance', '0')

        if int(route_id) == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        routes = Route.objects.filter(id=route_id)
        if routes.count() == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        route = routes.first()
        route.admin_id = member.admin_id
        route.member_id = member_id
        try:
            assign_id = request.POST.get('assign_id', '0')
            route.assign_id = assign_id
        except KeyError:
            print('no key')
            route.assign_id = '0'
        if name != '':
            route.name = name
        route.description = description
        route.admin_desc = description
        route.start_time = start_time
        route.end_time = end_time
        route.duration = duration
        route.speed = speed
        route.distance = distance
        route.reported_time = str(int(round(time.time() * 1000)))
        route.status = 'reported'
        route.save()

        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp))



import pandas as pd

@api_view(['GET', 'POST'])
def updateroutepoints(request):
    if request.method == 'POST':

        route_id = request.POST.get('route_id', '0')

        member_id = request.POST.get('member_id', '0')
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        start_time = request.POST.get('start_time', '0')
        end_time = request.POST.get('end_time', '0')
        duration = request.POST.get('duration', '0')
        speed = request.POST.get('speed', '0')
        distance = request.POST.get('distance', '0')

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        if int(route_id) == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        routes = Route.objects.filter(id=route_id)
        if routes.count() == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        route = routes.first()
        route.admin_id = member.admin_id
        route.member_id = member_id
        try:
            assign_id = request.POST.get('assign_id', '0')
            route.assign_id = assign_id
        except KeyError:
            print('no key')
            route.assign_id = '0'
        if name != '':
            route.name = name
        route.description = description
        route.admin_desc = description
        route.start_time = start_time
        route.end_time = end_time
        route.duration = duration
        route.speed = speed
        route.distance = distance
        route.reported_time = str(int(round(time.time() * 1000)))
        route.save()

        folder = settings.MEDIA_ROOT + '/points/'

        fs = FileSystemStorage(location=folder)

        file = request.FILES['jsonfile']

        file_path = 'route_' + str(route.pk) + '.json'

        newPointList = parseJson(file)

        f = fs.open(file_path, 'rt')
        oldPointList = json.loads(f.read())['points']
        for p in newPointList:
            if len(oldPointList) > 0:
                p['id'] = str(int(oldPointList[len(oldPointList) - 1]['id']) + 1)
            oldPointList.append(p)
        f.close()
        f = fs.open(file_path, 'w')
        f.write(json.dumps({'points':RpointSerializer(oldPointList, many=True).data}))

        # new_data = json.dumps(json.load(file))
        # if new_data != '':
        #     f = fs.open(file_path, 'rt')
        #     fread = json.dumps(json.loads(f.read()))
        #     fread = fread.strip().replace(" ","")
        #     # if fread.endswith(']}') == False or fread.count(']}') > 1:
        #     #     indx = fread.find(']}')
        #     #     fread = fread[0: indx + 2]
        #     fdata = ''
        #     # if fread.startswith('{"points":') == False and fread.startswith('{\'points\':') == False: fdata = new_data
        #     # else: fdata = fread.replace(']}',',') + new_data.replace('{"points": [','').replace('{"points":[','').replace('{\'points\': [','').replace('{\'points\':[','')
        #     if fread.startswith('{"points":') == True and fread.endswith("]}") == True:
        #         fdata = fread[:-2] + ',' + new_data.strip().replace(" ","")[11:]
        #     f.close()
        #     if fdata != '':
        #         f = fs.open(file_path, 'w')
        #         f.write(fdata)

        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp))



def jsonStr(p_f):
    points = ''
    for line in p_f:
        decoded_line = line.decode("utf-8")
        points += decoded_line
    if points != '':
        points = points.replace('\\','')
    return points




def parseJson(p_f):
    pointList = []
    points = ''
    for line in p_f:
        decoded_line = line.decode("utf-8")
        points += decoded_line
    if points != '':
        points = points.replace('\\','')
        try:
            decoded = json.loads(points)
            pointList = decoded['points']
        except:
            print('Point data parse error')

    return pointList



















































































































