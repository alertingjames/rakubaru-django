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
import unicodecsv as csv
from io import BytesIO
import redislite

from rakubaru.models import Rmember, Route, Rpoint, Rpin, Paid, Device, Coupon, Area, Sublocality, AreaAssign, Product, Price, Invoice, Plan, PointJsonData, PointData
from rakubaru.serializers import RmemberSerializer, RouteSerializer, RpointSerializer, RpinSerializer, AreaSerializer, SublocalitySerializer, AreaAssignSerializer



def userscsvexport(request):

    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response, encoding='utf-8-sig')
    writer.writerow(['名前', 'Eメール', '電話番号', '役割'])

    users = Rmember.objects.filter(admin_id=adminID).values_list('name','email', 'phone_number', 'role')
    for user in users:
        writer.writerow(user)

    return response



def reportscsvexport(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'

    writer = csv.writer(response, encoding='utf-8-sig')
    writer.writerow(['題名', '説明', '開始時間', '終了時間', '配布時間', '平均速度(km/時)', '移動距離(km)', '報告された時間', 'エリア名', 'アサイン時タイトル'])

    routes = Route.objects.filter(admin_id=adminID, status='reported').order_by('-id')
    for route in routes:
        members = Rmember.objects.filter(admin_id=adminID, id=int(route.member_id))
        if members.count() > 0:
            assigns = AreaAssign.objects.filter(id=route.assign_id)
            if assigns.count() > 0:
                assign = assigns[0]
                area = Area.objects.get(id=assign.area_id)
                route.area_name = area.area_name
                route.assign_title = assign.title

            route.start_time = datetime.datetime.fromtimestamp(float(int(route.start_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.end_time = datetime.datetime.fromtimestamp(float(int(route.end_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.reported_time = datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.speed = round(float(route.speed), 2)
            route.distance = round(float(route.distance), 3)
            con_sec, con_min, con_hour = convertMillis(int(route.duration))
            route.duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

            if float(route.distance) == 0:
                route.speed = '0.0'

            writer.writerow([route.name, route.admin_desc, route.start_time, route.end_time, route.duration, route.speed, route.distance, route.reported_time, route.area_name, route.assign_title])

    return response


def convertMillis(millis):
     seconds=(millis/1000)%60
     minutes=(millis/(1000*60))%60
     hours=(millis/(1000*60*60))%24
     return seconds, minutes, hours



def assignscsvexport(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="distributes.csv"'

    writer = csv.writer(response, encoding='utf-8-sig')
    writer.writerow(['id', '会員', 'タイトル', 'エリア名', '配布部数', '全体距離(km)', '配布距離(km)', '配布物', '配布期間（開始日）', '配布期間（終了日）', '配布回数', '進捗', '配布単価', '手当', \
         '金額', '距離(km)', '顧客名', '割り当て時間'])

    assigns = AreaAssign.objects.filter(admin_id=adminID).order_by('-id')
    i = 0
    for assign in assigns:
        areas = Area.objects.filter(id=assign.area_id)
        if areas.count() > 0:
            area = areas[0]
            members = Rmember.objects.filter(id=assign.member_id)
            if members.count() > 0:
                i += 1
                member = members[0]
                routes = Route.objects.filter(member_id=member.pk, assign_id=assign.pk, status='reported')
                works = routes.count()
                distance = 0
                for route in routes:
                    distance = distance + float(route.distance)
                assigned_distance = area.distance
                progress = 0
                if float(assigned_distance) > 0:
                    progress = round(float(distance * 100 / float(assigned_distance)), 2)
                assign.client_dist = round(distance, 2)

                dist_start_time = ' --- '
                dist_end_time = ' --- '
                if assign.start_time != '' and assign.start_time != '0':
                    dist_start_time = datetime.datetime.fromtimestamp(float(int(assign.start_time)/1000)).strftime("%m/%d/%y")
                if assign.end_time != '' and assign.end_time != '0':
                    dist_end_time = datetime.datetime.fromtimestamp(float(int(assign.end_time)/1000)).strftime("%m/%d/%y")

                assigned = datetime.datetime.fromtimestamp(float(int(assign.assigned_time)/1000)).strftime("%m/%d/%y %H:%M")

                writer.writerow([str(i), member.name, assign.title, area.area_name, assign.copies, area.distance, assign.client_dist, assign.distribution, dist_start_time, \
                    dist_end_time, works, progress, assign.unit_price, assign.allowance, assign.amount, assign.distance, assign.customer, assigned])

    return response




def csvexport(request):
    import datetime
    route_id = request.GET['route_id']

    routes = Route.objects.filter(id=route_id)
    if routes.count() > 0:
        route = routes.first()
        members = Rmember.objects.filter(id=int(route.member_id))
        if members.count() > 0:
            assigns = AreaAssign.objects.filter(id=route.assign_id)
            if assigns.count() > 0:
                assign = assigns[0]
                area = Area.objects.get(id=assign.area_id)
                route.area_name = area.area_name
                route.assign_title = assign.title

            route.start_time = datetime.datetime.fromtimestamp(float(int(route.start_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.end_time = datetime.datetime.fromtimestamp(float(int(route.end_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.reported_time = datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.speed = round(float(route.speed), 2)
            route.distance = round(float(route.distance), 3)
            con_sec, con_min, con_hour = convertMillis(int(route.duration))
            route.duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

            if float(route.distance) == 0:
                route.speed = '0.0'

            response = HttpResponse(content_type='text/csv')
            filename = 'report_routes_' + route.name + '.csv'
            from urllib.parse import quote
            file_expr = "filename*=utf-8''{}".format(quote(filename))
            response['Content-Disposition'] = 'attachment; {}'.format(file_expr)

            writer = csv.writer(response, encoding='utf-8-sig')
            writer.writerow(['題名', '説明', '開始時間', '終了時間', '配布時間', '平均速度(km/時)', '移動距離(km)', '報告された時間', 'エリア名', 'アサイン時タイトル'])

            writer.writerow([route.name, route.admin_desc, route.start_time, route.end_time, route.duration, route.speed, route.distance, route.reported_time, route.area_name, route.assign_title])

            return response

        return HttpResponse('The owner of the report does not exist.')

    return HttpResponse('The report does not exist.')



def jsonexport(request):
    import datetime
    route_id = request.GET['route_id']

    routes = Route.objects.filter(id=route_id)
    if routes.count() > 0:
        route = routes.first()
        members = Rmember.objects.filter(id=route.member_id)
        if members.count() > 0:
            assigns = AreaAssign.objects.filter(id=route.assign_id)
            if assigns.count() > 0:
                assign = assigns[0]
                area = Area.objects.get(id=assign.area_id)
                route.area_name = area.area_name
                route.assign_title = assign.title

            route.start_time = datetime.datetime.fromtimestamp(float(int(route.start_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.end_time = datetime.datetime.fromtimestamp(float(int(route.end_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.reported_time = datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.speed = round(float(route.speed), 2)
            route.distance = round(float(route.distance), 3)
            con_sec, con_min, con_hour = convertMillis(int(route.duration))
            route.duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

            if float(route.distance) == 0:
                route.speed = '0.0'
                # route.duration = '00h 00m 00s'

            data = {
                '題名': route.name,
                '説明': route.admin_desc,
                '開始時間': route.start_time,
                '終了時間': route.end_time,
                '配布時間': route.duration,
                '平均速度(km/時)': route.speed,
                '移動距離(km)': route.distance,
                '報告された時間': route.reported_time,
                'エリア名': route.area_name,
                'アサイン時タイトル': route.assign_title,
            }

            json_str = json.dumps(data, ensure_ascii=False).encode('utf-8-sig')

            response = HttpResponse(json_str, content_type='application/json')
            filename = 'report_routes_' + route.name + '.json'
            from urllib.parse import quote
            file_expr = "filename*=utf-8''{}".format(quote(filename))
            response['Content-Disposition'] = 'attachment; {}'.format(file_expr)
            return response

        return HttpResponse('The owner of the report does not exist.')

    return HttpResponse('The report does not exist.')



def assignreportscsvexport(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="assigned_reports.csv"'

    writer = csv.writer(response, encoding='utf-8-sig')
    writer.writerow(['題名', '説明', '開始時間', '終了時間', '配布時間', '平均速度(km/時)', '移動距離(km)', '報告された時間', 'エリア名', 'アサイン時タイトル'])

    assign_id = request.GET['assign_id']
    member_id = request.GET['member_id']

    assign = AreaAssign.objects.get(id=assign_id)
    routes = Route.objects.filter(member_id=member_id, assign_id=assign_id, status='reported').order_by('-id')
    for route in routes:
        members = Rmember.objects.filter(admin_id=adminID, id=int(route.member_id))
        if members.count() > 0:
            area = Area.objects.get(id=assign.area_id)
            route.area_name = area.area_name
            route.assign_title = assign.title

            route.start_time = datetime.datetime.fromtimestamp(float(int(route.start_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.end_time = datetime.datetime.fromtimestamp(float(int(route.end_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.reported_time = datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.speed = round(float(route.speed), 2)
            route.distance = round(float(route.distance), 3)
            con_sec, con_min, con_hour = convertMillis(int(route.duration))
            route.duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

            if float(route.distance) == 0:
                route.speed = '0.0'

            writer.writerow([route.name, route.admin_desc, route.start_time, route.end_time, route.duration, route.speed, route.distance, route.reported_time, route.area_name, route.assign_title])

    return response


@api_view(['POST', 'GET'])
def viewreport(request):
    jsonstr = request.POST.get('data','')
    if jsonstr != '':
        try:
            decoded = json.loads(jsonstr)
            route = decoded['route']
            pnts = decoded['points']
            pins = decoded['pins']
            area = decoded['area']
            sublocs = decoded['sublocs']

            data = {
                'route':route,
                'points':pnts,
                'pins':pins,
                'area': area,
                'sublocs': sublocs,
            }
            context = {
                'report': data
            }
            return render(request, 'rakubaru/data_disp.html', context)
        except:
            print('Data parsing error')

    return render(request, 'rakubaru/data_disp.html')



def data_backup(request):
    import datetime
    route_id = request.GET['route_id']

    routes = Route.objects.filter(id=route_id)
    if routes.count() > 0:
        route = routes.first()
        members = Rmember.objects.filter(id=route.member_id)
        if members.count() > 0:
            assigns = AreaAssign.objects.filter(id=route.assign_id)
            if assigns.count() > 0:
                assign = assigns[0]
                area = Area.objects.get(id=assign.area_id)
                route.area_name = area.area_name
                route.assign_title = assign.title

            route.start_time = datetime.datetime.fromtimestamp(float(int(route.start_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.end_time = datetime.datetime.fromtimestamp(float(int(route.end_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.reported_time = datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%m/%d/%y %H:%M")
            route.speed = round(float(route.speed), 2)
            route.distance = round(float(route.distance), 3)
            con_sec, con_min, con_hour = convertMillis(int(route.duration))
            route.duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

            if float(route.distance) == 0:
                route.speed = '0.0'
                # route.duration = '00h 00m 00s'

            pnts = []
            pointlist = routefilepoints(route_id)
            if len(pointlist) > 0:
                pnts = pointlist
            else:
                folder = settings.MEDIA_ROOT + '/points/'
                fs = FileSystemStorage(location=folder)
                file_path = 'route_' + str(route_id) + '.json'

                pjds = PointJsonData.objects.filter(route_id=route_id)
                if pjds.count() > 0:
                    pjd = pjds.first()
                    if pjd.points_json != '':
                        pnts = pjd.points_json
                        pnts = json.loads(pnts)
                else:
                    pjds = PointData.objects.filter(route_id=route_id)
                    if pjds.count() > 0:
                        pjd = pjds.first()
                        if pjd.points_json != '':
                            pnts = pjd.points_json
                            pnts = json.loads(pnts)
                    else:
                        pnts = Rpoint.objects.filter(route_id=route_id)
                f = fs.open(file_path, 'w+')
                f.write(json.dumps({'points':RpointSerializer(pnts, many=True).data}))

            pins = Rpin.objects.filter(member_id=route.member_id)
            for pin in pins:
                pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')

            area = None
            sublocs = []
            if int(route.assign_id) > 0:
                assign = AreaAssign.objects.get(id=route.assign_id)
                area = Area.objects.get(id=assign.area_id)
                sublocs = Sublocality.objects.filter(area_id=area.pk)
                for subloc in sublocs:
                    subloc.locarr = subloc.locarr.replace("'","")

            data = {
                '題名': route.name,
                '説明': route.admin_desc,
                '開始時間': route.start_time,
                '終了時間': route.end_time,
                '配布時間': route.duration,
                '平均速度(km/時)': route.speed,
                '移動距離(km)': route.distance,
                '報告された時間': route.reported_time,
                'エリア名': route.area_name,
                'アサイン時タイトル': route.assign_title,
                'route':RouteSerializer(route, many=False).data,
                'points':RpointSerializer(pnts, many=True).data,
                'pins': RpinSerializer(pins, many=True).data,
                'area': AreaSerializer(area, many=False).data,
                'sublocs': SublocalitySerializer(sublocs, many=True).data,
            }

            json_str = json.dumps(data, ensure_ascii=False).encode('utf-8-sig')

            response = HttpResponse(json_str, content_type='application/json')
            filename = 'report_' + route.name + '.json'
            from urllib.parse import quote
            file_expr = "filename*=utf-8''{}".format(quote(filename))
            response['Content-Disposition'] = 'attachment; {}'.format(file_expr)
            return response

        return HttpResponse('The owner of the report does not exist.')

    return HttpResponse('The report does not exist.')




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



def routefilepoints(route_id):
    folder = settings.MEDIA_ROOT + '/points/'
    fs = FileSystemStorage(location=folder)
    file_path = 'route_' + str(route_id) + '.json'
    if fs.exists(file_path) == True:
        f = fs.open(file_path)
        # pointList = parseJson(f)
        pointList = json.loads(f.read())['points']
        return pointList
    else:
        return []




def exportassignedworksjson(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    assign_id = request.GET['assign_id']
    member_id = request.GET['member_id']
    assign = AreaAssign.objects.get(id=assign_id)

    routes = Route.objects.filter(member_id=member_id, assign_id=assign_id, status='reported')
    routeList = []
    speed = 0
    distance = 0
    duration = 0
    for route in routes:
        pnts = []
        pointlist = routefilepoints(route.pk)
        if len(pointlist) > 0:
            pnts = pointlist
        else:
            folder = settings.MEDIA_ROOT + '/points/'
            fs = FileSystemStorage(location=folder)
            file_path = 'route_' + str(route.pk) + '.json'

            pjds = PointJsonData.objects.filter(route_id=route.pk)
            if pjds.count() > 0:
                pjd = pjds.first()
                if pjd.points_json != '':
                    pnts = pjd.points_json
                    pnts = json.loads(pnts)
            else:
                pjds = PointData.objects.filter(route_id=route.pk)
                if pjds.count() > 0:
                    pjd = pjds.first()
                    if pjd.points_json != '':
                        pnts = pjd.points_json
                        pnts = json.loads(pnts)
                else:
                    pnts = Rpoint.objects.filter(route_id=route.pk)
            f = fs.open(file_path, 'w+')
            f.write(json.dumps({'points':RpointSerializer(pnts, many=True).data}))

        data = {
            'route': RouteSerializer(route, many=False).data,
            'points': RpointSerializer(pnts, many=True).data,
        }
        routeList.append(data)

        distance += float(route.distance)
        duration += int(route.duration)

    if duration > 0: speed = float(distance / duration) * 3600 * 1000

    avg_speed = round(speed, 2)
    total_distance = round(distance, 3)
    con_sec, con_min, con_hour = convertMillis(duration)
    total_duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

    route = routes.first()
    pins = Rpin.objects.filter(member_id=route.member_id)
    for pin in pins:
        pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')

    area = None
    sublocs = []
    if int(route.assign_id) > 0:
        assign = AreaAssign.objects.get(id=route.assign_id)
        area = Area.objects.get(id=assign.area_id)
        sublocs = Sublocality.objects.filter(area_id=area.pk)
        for subloc in sublocs:
            subloc.locarr = subloc.locarr.replace("'","").replace("\\","")

    data = {
        'assign':AreaAssignSerializer(assign, many=False).data,
        'routes':routeList,
        'pins':RpinSerializer(pins, many=True).data,
        'area': AreaSerializer(area, many=False).data,
        'sublocs': SublocalitySerializer(sublocs, many=True).data,
        'speed': avg_speed,
        'distance': total_distance,
        'duration': total_duration,
    }

    json_str = json.dumps(data, ensure_ascii=False).encode('utf-8-sig')

    response = HttpResponse(json_str, content_type='application/json')
    filename = 'assigned_works.json'
    from urllib.parse import quote
    file_expr = "filename*=utf-8''{}".format(quote(filename))
    response['Content-Disposition'] = 'attachment; {}'.format(file_expr)
    return response






















































######################### Test ########################################################


from django.core.exceptions import ObjectDoesNotExist
def delxxxroutes(request):
    pjds = PointJsonData.objects.all()
    for pjd in pjds:
        try:
            route = Route.objects.get(id=pjd.route_id)
        except ObjectDoesNotExist:
            print('No key')
            # points = Rpoint.objects.filter(route_id=route.pk)
            # points.delete()
            # pins = Rpin.objects.filter(route_id=route.pk)
            # pins.delete()
            # pjds = PointJsonData.objects.filter(route_id=route.pk)
            pjd.delete()

    return HttpResponse('Success!')


def pntcount(request):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('''SELECT count(*) FROM rakubaru_rpoint''')
    row = cursor.fetchone()
    # pnt_count = Rpoint.objects.all().count()
    return HttpResponse('PNTs: ' + str(row))



def jsontest(request):
    pnts = Rpoint.objects.filter(route_id=7471)
    ser = RpointSerializer(pnts, many=True)
    json_str = json.dumps(ser.data)
    response = HttpResponse(json_str, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=routes.json'
    return response


def routeadminset(request):
    routes = Route.objects.all()
    for route in routes:
        members = Rmember.objects.filter(id=route.member_id)
        if members.count() > 0:
            member = members.first()
            route.admin_id = member.admin_id
            route.save()
    return HttpResponse('success')



def take_screenshot(request):
    BASE = 'https://render-tron.appspot.com/screenshot/'
    url = 'https://www.rakubaru-posting.com/'
    path = 'target.jpg'
    parameters = {
        'fullpage': True
    }
    response = requests.get(BASE + url, stream=True, params=parameters)
    # save file, see https://stackoverflow.com/a/13137873/7665691
    if response.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in response:
                file.write(chunk)
    return HttpResponse('success')


import redis
def toroutemap(request):
    import datetime
    route_id = request.GET['route_id']
    routes = Route.objects.filter(id=route_id)

    if routes.count() > 0:
        route = routes.first()
        members = Rmember.objects.filter(id=route.member_id)
        if members.count() > 0:
            member = members[0]
            route.name = member.name + '_' + datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%y%m%d_%H%M")

        route.start_time = datetime.datetime.fromtimestamp(float(int(route.start_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.end_time = datetime.datetime.fromtimestamp(float(int(route.end_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.reported_time = datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.speed = round(float(route.speed), 2)
        route.distance = round(float(route.distance), 3)
        con_sec, con_min, con_hour = convertMillis(int(route.duration))
        route.duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

        if float(route.distance) == 0:
            route.speed = '0.0'
            # route.duration = '00h 00m 00s'

        # pnts = Rpoint.objects.filter(route_id=route.pk)
        # data = {
        #     'route':route,
        #     'points':pnts,
        # }
        # return render(request, 'rakubaru/route_map.html', {'report':data})

        r = redis.Redis(host='redis-19364.c256.us-east-1-2.ec2.cloud.redislabs.com', port=19364, password='J4LRAO85HtZsPk4jTnMJKYkjo2fWJJll')
        pnts = r.get('route' + str(route_id))
        if not pnts is None:
            # return HttpResponse(str(len(pnts)))
            data = {
                'route':route,
                'points':json.loads(pnts),
            }
            return render(request, 'rakubaru/route_map.html', {'report':data})
        else:
            pnts = Rpoint.objects.filter(route_id=route.pk)
            pointList = []
            for pnt in pnts:
                jdt = {
                    'id': pnt.pk,
                    'route_id': pnt.route_id,
                    'lat': pnt.lat,
                    'lng': pnt.lng,
                    'comment': pnt.comment,
                    'time': pnt.time,
                    'color': pnt.color,
                    'status': pnt.status
                }
                pointList.append(jdt)
            r.set('route' + str(route_id), json.dumps(pointList))
            data = {
                'route':route,
                'points':pointList,
            }
            return render(request, 'rakubaru/route_map.html', {'report':data})



def tomapshot(request):
    return render(request, 'rakubaru/route_map_shot.html')




def redistestforroutepoints(request):
    import datetime
    route_id = request.GET['route_id']
    routes = Route.objects.filter(id=route_id)

    if routes.count() > 0:
        route = routes.first()
        members = Rmember.objects.filter(id=route.member_id)
        if members.count() > 0:
            member = members[0]
            route.name = member.name + '_' + datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%y%m%d_%H%M")

        route.start_time = datetime.datetime.fromtimestamp(float(int(route.start_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.end_time = datetime.datetime.fromtimestamp(float(int(route.end_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.reported_time = datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.speed = round(float(route.speed), 2)
        route.distance = round(float(route.distance), 3)
        con_sec, con_min, con_hour = convertMillis(int(route.duration))
        route.duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

        if float(route.distance) == 0:
            route.speed = '0.0'
            # route.duration = '00h 00m 00s'

        pjds = PointJsonData.objects.filter(route_id=route.pk)
        if pjds.count() > 0:
            pjd = pjds.first()
            if pjd.points_json != '':
                pnts = pjd.points_json
                data = {
                    'route':route,
                    'points':json.loads(pnts),
                }
                return render(request, 'rakubaru/route_map.html', {'report':data})
        else:
            pnts = Rpoint.objects.filter(route_id=route.pk)
            pjd = PointJsonData()
            pjd.route_id = route.pk
            pjd.points_json = json.dumps(RpointSerializer(pnts, many=True).data)
            pjd.save()

            data = {
                'route':route,
                'points':pnts,
            }
            return render(request, 'rakubaru/route_map.html', {'report':data})

        # try:
        #     pnts = request.session['route' + str(route_id)]
        #     # return HttpResponse(str(pnts))
        #     data = {
        #         'route':route,
        #         'points':pnts,
        #     }
        #     return render(request, 'rakubaru/route_map.html', {'report':data})
        # except KeyError:
        #     print('No key')

        # pnts = Rpoint.objects.filter(route_id=route.pk)
        # request.session['route' + str(route_id)] = RpointSerializer(pnts, many=True).data
        # data = {
        #     'route':route,
        #     'points':pnts,
        # }
        # return render(request, 'rakubaru/route_map.html', {'report':data})























































































