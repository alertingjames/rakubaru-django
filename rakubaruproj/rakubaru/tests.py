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



def points_count(request):
    return HttpResponse('points: ' + str(Rpoint.objects.all().count()))


@api_view(['GET', 'POST'])
def save_route(request):
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
        pulse = request.POST.get('pulse', '0')
        sts = request.POST.get('status', '')

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        route = None
        if int(route_id) > 0:
            route = Route.objects.get(id=route_id)
        else:
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
        if sts == 'report': route.status = 'reported'
        route.save()

        if sts != 'report_end':
            lat = request.POST.get('lat', '0')
            lng = request.POST.get('lng', '0')
            comment = request.POST.get('comment', '')
            color = request.POST.get('color', '')
            tm = str(int(round(time.time() * 1000)))

            pjds = PointJsonData.objects.filter(route_id=route.pk)
            if pjds.count() > 0:
                pjd = pjds.first()
                if pjd.points_json != '':
                    pointList = json.loads(pjd.points_json)
                    pnt = Rpoint()
                    pnt.id = int(pointList[len(pointList) - 1]['id']) + 1
                    pnt.route_id = route.pk
                    pnt.lat = lat
                    pnt.lng = lng
                    pnt.comment = comment
                    pnt.color = color
                    pnt.time = tm
                    pointList.append(RpointSerializer(pnt, many=False).data)
                    pjd.points_json = json.dumps(RpointSerializer(pointList, many=True).data)
                    pjd.save()
            else:
                pnts = []
                pnt = Rpoint()
                pnt.id = 1
                pnt.route_id = route.pk
                pnt.lat = lat
                pnt.lng = lng
                pnt.comment = comment
                pnt.color = color
                pnt.time = tm
                pnts.append(pnt)
                pjd = PointJsonData()
                pjd.route_id = route.pk
                pjd.points_json = json.dumps(RpointSerializer(pnts, many=True).data)
                pjd.save()

        resp = {'result_code': '0', 'route_id': str(route.pk)}
        return HttpResponse(json.dumps(resp))








#################################################### Real Time Reporting From json file ###################################################################


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
            print('Point data saving error')

    return pointList



@api_view(['GET', 'POST'])
def updatereportofflinedata(request):
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
        pulse = request.POST.get('pulse', '0')
        sts = request.POST.get('status', '')

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        route = None
        if int(route_id) > 0:
            route = Route.objects.get(id=route_id)
        else:
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
        if sts == 'report': route.status = 'reported'
        route.save()

        folder = settings.MEDIA_ROOT + '/points/'
        fs = FileSystemStorage(location=folder)

        file = request.FILES['jsonfile']
        newPointList = parseJson(file)

        file_path = 'route_' + str(route_id) + '.json'

        pjds = PointJsonData.objects.filter(route_id=route.pk)
        pjd = None
        if pjds.count() > 0:
            pjd = pjds.first()
            oldPointList = json.loads(pjd.points_json)
            for p in newPointList:
                if len(oldPointList) > 0:
                    p['id'] = str(int(oldPointList[len(oldPointList) - 1]['id']) + 1)
                oldPointList.append(p)
            pjd.points_json = json.dumps(RpointSerializer(oldPointList, many=True).data)
            pjd.save()
        else:
            pjd = PointJsonData()
            pjd.route_id = route.pk
            pjd.points_json = json.dumps(RpointSerializer(newPointList, many=True).data)
            pjd.save()

        if pulse == '1':
            if pjd is not None:
                pointList = json.loads(pjd.points_json)
                f = fs.open(file_path, 'w+')
                f.write(json.dumps({'points':RpointSerializer(pointList, many=True).data}))

                pjd.delete()

        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def updatereportdatainrealtime(request):
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
        pulse = request.POST.get('pulse', '0')
        sts = request.POST.get('status', '')

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        if int(route_id) == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        route = None
        route = Route.objects.get(id=route_id)

        if route is None:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

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
        if sts == 'report': route.status = 'reported'
        route.save()

        folder = settings.MEDIA_ROOT + '/points/'

        fs = FileSystemStorage(location=folder)

        file = request.FILES['jsonfile']
        newPointList = parseJson(file)

        file_path = 'route_' + str(route_id) + '.json'

        if fs.exists(file_path) == False:
            filename = fs.save(file_path, file)
        else:
            f = fs.open(file_path)
            oldPointList = json.loads(f.read())['points']
            for p in newPointList:
                if len(oldPointList) > 0:
                    p['id'] = str(int(oldPointList[len(oldPointList) - 1]['id']) + 1)
                oldPointList.append(p)
            f.close()
            f = fs.open(file_path, 'w')
            f.write(json.dumps({'points':RpointSerializer(oldPointList, many=True).data}))


        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp))



#################################################### Start Or End Reporting #########################################################################################################################################


@api_view(['GET', 'POST'])
def startorendreporting(request):
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
        pulse = request.POST.get('pulse', '0')
        sts = request.POST.get('status', '')

        if int(duration) > 0 and int(route_id) == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        route = None
        if int(route_id) > 0:
            route = Route.objects.get(id=route_id)
        else:
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
        if sts == 'report': route.status = 'reported'
        route.save()

        resp = {'result_code': '0', 'route_id': str(route.pk)}
        return HttpResponse(json.dumps(resp))




################################################# Beta #####################################################################################################################################

def parseJsonStr(jsonstr):
    pointList = []
    if jsonstr != '':
        jsonstr = jsonstr.replace('\\','')
        try:
            decoded = json.loads(jsonstr)
            pointList = decoded['points']
        except:
            print('Point data saving error')

    return pointList


@api_view(['GET', 'POST'])
def xxxsaveroutexxx(request):
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
        pulse = request.POST.get('pulse', '0')
        sts = request.POST.get('status', '')

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        if int(route_id) == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        route = None
        route = Route.objects.get(id=route_id)

        if route is None:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

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
        if sts == 'report': route.status = 'reported'
        route.save()

        folder = settings.MEDIA_ROOT + '/points/'

        fs = FileSystemStorage(location=folder)

        jsonstr = request.POST.get('jsonstr', '')
        newPointList = parseJsonStr(jsonstr)

        file_path = 'route_' + str(route_id) + '.json'

        if fs.exists(file_path) == False:
            f = fs.open(file_path, 'w+')
            f.write(json.dumps({'points':RpointSerializer(newPointList, many=True).data}))
        else:
            f = fs.open(file_path)
            oldPointList = json.loads(f.read())['points']
            for p in newPointList:
                if len(oldPointList) > 0:
                    p['id'] = str(int(oldPointList[len(oldPointList) - 1]['id']) + 1)
                oldPointList.append(p)
            f.close()
            f = fs.open(file_path, 'w')
            f.write(json.dumps({'points':RpointSerializer(oldPointList, many=True).data}))


        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp))











################################################## Test ########################################################################################################################################


def jsonfiletest(request):

    newJS = '{"points":[{"id":"0","route_id":"10968","lat":"42.8931257","lng":"129.4564392","comment":"","color":"#e60012","time":"1631461569675","status":""},{"id":"1","route_id":"10968","lat":"42.8931164","lng":"129.4564866","comment":"","color":"#e60012","time":"1631461579727","status":""},{"id":"2","route_id":"10968","lat":"42.8931204","lng":"129.4564748","comment":"","color":"#e60012","time":"1631461589765","status":""},{"id":"3","route_id":"10968","lat":"42.8931164","lng":"129.4564832","comment":"","color":"#e60012","time":"1631461599808","status":""},{"id":"4","route_id":"10968","lat":"42.8931161","lng":"129.4564838","comment":"","color":"#e60012","time":"1631461609848","status":""},{"id":"5","route_id":"10968","lat":"42.8931156","lng":"129.4564851","comment":"","color":"#e60012","time":"1631461619903","status":""},{"id":"6","route_id":"10968","lat":"42.8931156","lng":"129.4564851","comment":"","color":"#e60012","time":"1631461619903","status":""},{"id":"7","route_id":"10968","lat":"42.8931198","lng":"129.4564759","comment":"","color":"#e60012","time":"1631461629946","status":""},{"id":"8","route_id":"10968","lat":"42.8931198","lng":"129.4564759","comment":"","color":"#e60012","time":"1631461629946","status":""},{"id":"9","route_id":"10968","lat":"42.8931147","lng":"129.4564889","comment":"","color":"#e60012","time":"1631461640003","status":""},{"id":"10","route_id":"10968","lat":"42.8931147","lng":"129.4564889","comment":"","color":"#e60012","time":"1631461640003","status":""},{"id":"11","route_id":"10968","lat":"42.8931164","lng":"129.4564831","comment":"","color":"#e60012","time":"1631461650050","status":""},{"id":"12","route_id":"10968","lat":"42.8931164","lng":"129.4564831","comment":"","color":"#e60012","time":"1631461650050","status":""},{"id":"13","route_id":"10968","lat":"42.8931196","lng":"129.4564763","comment":"","color":"#e60012","time":"1631461660099","status":""},{"id":"14","route_id":"10968","lat":"42.8931196","lng":"129.4564763","comment":"","color":"#e60012","time":"1631461660099","status":""},{"id":"15","route_id":"10968","lat":"42.8931192","lng":"129.4564768","comment":"","color":"#e60012","time":"1631461670145","status":""}]}'

    newPointList = json.loads(newJS)['points']

    folder = settings.MEDIA_ROOT + '/points/'

    fs = FileSystemStorage(location=folder)

    file_path = 'route_11015.json'

    f = fs.open(file_path)

    pnts = json.loads(f.read())['points']

    return HttpResponse(len(pnts))

    oldPointList = parseJson(f)

    for p in newPointList:
        if len(oldPointList) > 0:
            p['id'] = str(int(oldPointList[len(oldPointList) - 1]['id']) + 1)
        oldPointList.append(p)

    f.close()

    f = fs.open(file_path, 'w')
    f.write(json.dumps({'points':RpointSerializer(oldPointList, many=True).data}))

    return HttpResponse('success')




import redis

@api_view(['GET', 'POST'])
def zzzzzsaveroutezzz(request):
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
        pulse = request.POST.get('pulse', '0')
        sts = request.POST.get('status', '')

        members = Rmember.objects.filter(id=member_id)
        if members.count() == 0:
            resp = {'result_code': '-1'}
            return HttpResponse(json.dumps(resp))

        member = members.first()

        if int(route_id) == 0:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

        route = None
        route = Route.objects.get(id=route_id)

        if route is None:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))

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
        if sts == 'report': route.status = 'reported'
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

        r = redis.Redis(host='redis-19364.c256.us-east-1-2.ec2.cloud.redislabs.com', port=19364, password='J4LRAO85HtZsPk4jTnMJKYkjo2fWJJll')

        newPointList = []
        newPointList.append(RpointSerializer(pnt, many=False).data)

        r.set('route_' + str(route_id), json.dumps({'points':RpointSerializer(newPointList, many=True).data}))

        # resp = {'result_code': '0', 'data':r.get('route_' + str(route_id))}
        # return HttpResponse(json.dumps(resp))

        file_path = 'route_' + str(route_id) + '.json'

        if fs.exists(file_path) == False:
            f = fs.open(file_path, 'w+')
            f.write(str(r.get('route_' + str(route_id)), 'utf-8'))
            r.set('route_' + str(route_id), '')
        else:
            newPointList = json.loads(str(r.get('route_' + str(route_id)), 'utf-8'))['points']
            f = fs.open(file_path)
            oldPointList = json.loads(f.read())['points']
            for p in newPointList:
                if len(oldPointList) > 0:
                    p['id'] = str(int(oldPointList[len(oldPointList) - 1]['id']) + 1)
                oldPointList.append(p)
            f.close()
            f = fs.open(file_path, 'w')
            f.write(json.dumps({'points':RpointSerializer(oldPointList, many=True).data}))
            r.set('route_' + str(route_id), '')


        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp))






########################################################## Delete Routes ##########################################################################################

def rrreeessseeetttroute(request):
    routes = Route.objects.all()
    for route in routes:
        if int(route.reported_time) < 1631509200000:
            pins = Rpin.objects.filter(route_id=route.pk)
            pins.delete()
            # pjds = PointJsonData.objects.filter(route_id=route.pk)
            # pjds.delete()
            route.delete()

    return HttpResponse('Success!')



def delduplicates(request):

    folder = settings.MEDIA_ROOT + '/points/'
    fs = FileSystemStorage(location=folder)

    file_path = 'route_264987.json'
    if fs.exists(file_path) == True:
        f = fs.open(file_path, 'rt')
        fread = f.read()
        f.close()
        f = fs.open(file_path, 'w')
        f.write('{"points": [' + fread)

    return HttpResponse('Success!')






































