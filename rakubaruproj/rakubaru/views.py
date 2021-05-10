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

from rakubaru.models import Rmember, Route, Rpoint, Rpin, Paid, Device, Coupon, Area, Sublocality, AreaAssign, Product, Price
from rakubaru.serializers import RmemberSerializer, RouteSerializer, RpointSerializer, RpinSerializer, AreaSerializer, SublocalitySerializer, AreaAssignSerializer


#################### User ###############################################################################################################################


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        device = request.POST.get('device', '')

        if password != '':
            members = Rmember.objects.filter(email=email, password=password, role='')
        else:
            members = Rmember.objects.filter(email=email, role='')
        resp = {}
        if members.count() > 0:
            member = members[0]

            if member.status == '':
                member.status = 'loggedin'
                member.save()
            if device != '':
                devices = Device.objects.filter(member_id=member.pk, device=device)
                if devices.count() == 0:
                    dv = Device()
                    dv.member_id = member.pk
                    dv.device = device
                    dv.connected_time = str(int(round(time.time() * 1000)))
                    dv.status = 'in'
                    dv.save()
                else:
                    dv = devices[0]
                    dv.device = device
                    dv.connected_time = str(int(round(time.time() * 1000)))
                    dv.status = 'in'
                    dv.save()
                devices = Device.objects.filter(member_id=member.pk)
                for dv in devices:
                    if dv.device != device:
                        dv.status = 'out'
                        dv.save()

                member.device = device
                member.save()
            serializer = RmemberSerializer(member, many=False)
            resp = {'result_code': '0', 'data':serializer.data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)
        else:
            members = Rmember.objects.filter(email=email, role='')
            if members.count() > 0:
                resp = {'result_code': '2'}
            else: resp = {'result_code':'1'}

        return HttpResponse(json.dumps(resp))


@api_view(['POST', 'GET'])
def checkdevice(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '1')
        device = request.POST.get('device', '')

        devices = Device.objects.filter(member_id=member_id, device=device)
        if devices.count() > 0:
            dv = devices[0]
            return HttpResponse(json.dumps({'result_code':'0', 'status': dv.status}))

        else:
            if device != '':
                dv = Device()
                dv.member_id = member_id
                dv.device = device
                dv.connected_time = str(int(round(time.time() * 1000)))
                dv.status = 'in'
                dv.save()
                return HttpResponse(json.dumps({'result_code':'0', 'status': dv.status}))
            else:
                return HttpResponse(json.dumps({'result_code':'1'}))




@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        members = Rmember.objects.filter(email=email, role='')
        if members.count() == 0:
            return HttpResponse(json.dumps({'result_code': '1'}))

        member = members[0]

        message = 'こんにちは、パスワードを忘れた？。 では、アカウントのパスワードをリセットしますか？<br><br><a href="https://www.rakubaru-posting.com/rakubaru/resetpassword?uid=' + str(member.pk) + '">パスワードをリセットするには、このリンクをクリックしてください</a>'

        html =  """\
                    <html>
                        <head></head>
                        <body>
                            <h2 style="margin-left:10px; color:#02839a;">らくばるメンバーのセキュリティ更新情報</h2>
                            <div style="font-size:14px; word-wrap: break-word;">
                                {mes}
                            </div>
                        </body>
                    </html>
                """
        html = html.format(mes=message)

        fromEmail = settings.RAKUBARU_ADMIN_EMAIL
        toEmailList = []
        toEmailList.append(email)
        msg = EmailMultiAlternatives('パスワードのリセットを許可しました', '', fromEmail, toEmailList)
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)

        return HttpResponse(json.dumps({'result_code': '0'}))



def resetpassword(request):
    member_id = request.GET['uid']
    members = Rmember.objects.filter(id=int(member_id), role='')
    if members.count() > 0:
        member = members[0]
        return render(request, 'rakubaru/resetpwd.html', {'member':member})
    else:
        return render(request, 'rakubaru/result.html',
                          {'response': 'このメールは存在しません。 別のものを試してください。'})


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def rstpwd(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '1')
        password = request.POST.get('password', '')
        repassword = request.POST.get('repassword', '')
        if password != repassword:
            return render(request, 'rakubaru/result.html',
                          {'response': '同じパスワードを入力してください.'})
        members = Rmember.objects.filter(id=int(member_id))
        if members.count() > 0:
            member = members[0]
            member.password = password
            member.save()
            if member.role == 'admin':
                return render(request, 'rakubaru/admin.html', {'notify':'password changed'})
            return render(request, 'rakubaru/result.html',
                          {'response': 'パスワードは正常にリセットされました'})
        else:
            return render(request, 'rakubaru/result.html',
                          {'response': 'あなたは登録されていません'})



@api_view(['GET', 'POST'])
def updatemember(request):

    if request.method == 'POST':

        member_id = request.POST.get('member_id', '0')
        name = request.POST.get('name', '')
        phone_number = request.POST.get('phone_number', '')

        members = Rmember.objects.filter(id=int(member_id))
        count = members.count()
        if count > 0:

            member = members[0]
            member.name = name
            member.phone_number = phone_number
            member.save()

            fs = FileSystemStorage()

            i = 0
            for f in request.FILES.getlist('files'):
                # print("Product File Size: " + str(f.size))
                # if f.size > 1024 * 1024 * 2:
                #     continue
                i = i + 1
                filename = fs.save(f.name, f)
                uploaded_url = fs.url(filename)
                if i == 1:
                    member.picture_url = settings.URL + uploaded_url
                    member.save()

            serializer = RmemberSerializer(member, many=False)

            resp = {'result_code': '0', 'data':serializer.data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

        else:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))


@api_view(['GET', 'POST'])
def editmember(request):

    if request.method == 'POST':

        member_id = request.POST.get('member_id', '0')
        name = request.POST.get('name', '')
        phone_number = request.POST.get('phone_number', '')

        members = Rmember.objects.filter(id=int(member_id))
        count = members.count()
        if count > 0:

            member = members[0]
            member.name = name
            member.phone_number = phone_number
            member.save()

            fs = FileSystemStorage()

            try:
                image = request.FILES['file']
                filename = fs.save(image.name, image)
                uploaded_file_url = fs.url(filename)
                member.picture_url = settings.URL + uploaded_file_url
                member.save()
            except MultiValueDictKeyError:
                print('no file found')

            serializer = RmemberSerializer(member, many=False)

            resp = {'result_code': '0', 'data':serializer.data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)

        else:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))




@api_view(['GET', 'POST'])
def passwordupdate(request):

    if request.method == 'POST':

        member_id = request.POST.get('member_id', '0')
        password = request.POST.get('password', '')

        members = Rmember.objects.filter(id=int(member_id))
        count = members.count()
        if count > 0:

            member = members[0]
            member.password = password
            member.save()

            serializer = RmemberSerializer(member, many=False)

            resp = {'result_code': '0', 'data':serializer.data}
            return HttpResponse(json.dumps(resp), status=status.HTTP_200_OK)
        else:
            resp = {'result_code': '1'}
            return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def uploadroute(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '0')
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        start_time = request.POST.get('start_time', '0')
        end_time = request.POST.get('end_time', '0')
        duration = request.POST.get('duration', '0')
        speed = request.POST.get('speed', '0')
        distance = request.POST.get('distance', '0')

        sts = request.POST.get('status', '')

        points = request.POST.get('points', '')

        route = Route()
        route.member_id = member_id
        try:
            assign_id = request.POST.get('assign_id', '0')
            route.assign_id = assign_id
        except KeyError:
            print('no key')
            route.assign_id = '0'
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

        if points != '':
            try:
                decoded = json.loads(points)
                for data in decoded['points']:

                    lat = data['lat']
                    lng = data['lng']
                    comment = data['comment']
                    color = data['color']
                    tm = data['time']

                    pnt = Rpoint()
                    pnt.route_id = route.pk
                    pnt.lat = lat
                    pnt.lng = lng
                    pnt.comment = comment
                    pnt.color = color
                    pnt.time = tm
                    pnt.save()
            except:
                print('Point data saving error')
                resp = {'result_code': '1'}
                return HttpResponse(json.dumps(resp))

        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp))

#################################################### From json file ###################################################################

@api_view(['GET', 'POST'])
def upRoute(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '0')
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        start_time = request.POST.get('start_time', '0')
        end_time = request.POST.get('end_time', '0')
        duration = request.POST.get('duration', '0')
        speed = request.POST.get('speed', '0')
        distance = request.POST.get('distance', '0')

        sts = request.POST.get('status', '')

        fs = FileSystemStorage()

        file = request.FILES['jsonfile']

        points = ''

        for line in file:
        	decoded_line = line.decode("utf-8")
        	points = points + decoded_line

        route = Route()
        route.member_id = member_id
        try:
            assign_id = request.POST.get('assign_id', '0')
            route.assign_id = assign_id
        except KeyError:
            print('no key')
            route.assign_id = '0'
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

        if points != '':
            points = points.replace('\\','')
            try:
                decoded = json.loads(points)
                for data in decoded['points']:

                    lat = data['lat']
                    lng = data['lng']
                    comment = data['comment']
                    color = data['color']
                    tm = data['time']

                    pnt = Rpoint()
                    pnt.route_id = route.pk
                    pnt.lat = lat
                    pnt.lng = lng
                    pnt.comment = comment
                    pnt.color = color
                    pnt.time = tm
                    pnt.save()
            except:
                print('Point data saving error')
                resp = {'result_code': '1'}
                return HttpResponse(json.dumps(resp))

        resp = {'result_code': '0'}
        return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def getmyroutes(request):
    import datetime
    if request.method == 'POST':
        member_id = request.POST.get('member_id','1')
        members = Rmember.objects.filter(id=member_id)
        if members.count() > 0:
            member = members[0]
            routes = Route.objects.filter(member_id=member.pk).order_by('-id')
            # for route in routes:
            #     route.name = member.name + '_' + datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%y%m%d_%H%M")
            serializer = RouteSerializer(routes, many=True)
            resp = {'result_code':'0', 'data':serializer.data}
            return HttpResponse(json.dumps(resp))
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))


@api_view(['GET', 'POST'])
def routedetails(request):
    if request.method == 'POST':
        route_id = request.POST.get('route_id','1')
        pnts = Rpoint.objects.filter(route_id=route_id)
        pointser = RpointSerializer(pnts, many=True)
        resp = {'result_code':'0', 'points':pointser.data}
        return HttpResponse(json.dumps(resp))


@api_view(['GET', 'POST'])
def reportroute(request):
    if request.method == 'POST':
        route_id = request.POST.get('route_id','1')
        routes = Route.objects.filter(id=route_id)
        if routes.count() > 0:
            route = routes[0]
            route.status = 'reported'
            route.save()
            resp = {'result_code':'0'}
            return HttpResponse(json.dumps(resp))
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))


@api_view(['GET', 'POST'])
def delroute(request):
    if request.method == 'POST':
        route_id = request.POST.get('route_id','1')
        routes = Route.objects.filter(id=route_id)
        if routes.count() > 0:
            route = routes[0]
            route.status2 = 'deleted'
            route.save()
            # points = Rpoint.objects.filter(route_id=route.pk)
            # for pnt in points:
            #     pnt.delete()
            # pins = Rpin.objects.filter(route_id=route.pk)
            # for pin in pins:
            #     pin.delete()
            # route.delete()
            resp = {'result_code':'0'}
            return HttpResponse(json.dumps(resp))
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def savepin(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id', '0')
        pin_id = request.POST.get('pin_id', '0')
        lat = request.POST.get('lat', '0')
        lng = request.POST.get('lng', '0')
        comment = request.POST.get('comment', '')
        tm = request.POST.get('time', '0')

        pin = None
        if int(pin_id) > 0:
            pins = Rpin.objects.filter(id=int(pin_id))
            if pins.count() > 0:
                pin = pins[0]
            else:
                resp = {'result_code':'1'}
                return HttpResponse(json.dumps(resp))
        else:
            pin = Rpin()
            pin.member_id = member_id
        pin.lat = lat
        pin.lng = lng
        pin.comment = comment
        pin.time = tm
        pin.save()

        resp = {'result_code':'0', 'pin_id':str(pin.pk)}
        return HttpResponse(json.dumps(resp))


@api_view(['GET', 'POST'])
def getmypins(request):
    import datetime
    if request.method == 'POST':
        member_id = request.POST.get('member_id','1')
        members = Rmember.objects.filter(id=member_id)
        if members.count() > 0:
            member = members[0]
            pins = Rpin.objects.filter(member_id=member.pk)
            for pin in pins:
                pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r")
            pinser = RpinSerializer(pins, many=True)
            resp = {'result_code':'0', 'pins':pinser.data}
            return HttpResponse(json.dumps(resp))
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def delpin(request):
    if request.method == 'POST':
        pin_id = request.POST.get('pin_id','1')
        pins = Rpin.objects.filter(id=pin_id)
        if pins.count() > 0:
            pin = pins[0]
            pin.delete()
            resp = {'result_code':'0'}
            return HttpResponse(json.dumps(resp))
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def logout(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id','1')
        members = Rmember.objects.filter(id=member_id)
        if members.count() > 0:
            member = members[0]
            member.device = ''
            member.save()
            resp = {'result_code':'0'}
            return HttpResponse(json.dumps(resp))
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def checkrouteloading(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id','1')
        routes = Route.objects.filter(member_id=member_id).order_by('-id')
        if routes.count() > 0:
            route = routes[0]
            points = Rpoint.objects.filter(route_id=route.pk)
            resp = {'result_code':'0', 'points': str(points.count())}
            return HttpResponse(json.dumps(resp))
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))


@api_view(['GET', 'POST'])
def getAssignedAreas(request):
    member_id = request.GET['member_id']
    assigns = AreaAssign.objects.filter(member_id=member_id).order_by('-id')
    list = []
    for assign in assigns:
        if assign.status != 'deleted':
            area = Area.objects.get(id=assign.area_id)
            areaser = AreaSerializer(area, many=False)
            assignser = AreaAssignSerializer(assign, many=False)
            data = {
                'area':areaser.data,
                'assign':assignser.data
            }
            list.append(data)
    return HttpResponse(json.dumps({'result_code':'0', 'data':list}))



@api_view(['GET', 'POST'])
def removeAssign(request):
    assign_id = request.GET['assign_id']
    assign = AreaAssign.objects.get(id=assign_id)
    assign.status = 'deleted'
    assign.save()
    return HttpResponse(json.dumps({'result_code':'0'}))


@api_view(['GET', 'POST'])
def getAreaSublocs(request):
    assign_id = request.GET['assign_id']
    assigns = AreaAssign.objects.filter(id=assign_id)
    if assigns.count() > 0:
        assign = assigns[0]
        sublocs = Sublocality.objects.filter(area_id=assign.area_id)
        sublocser = SublocalitySerializer(sublocs, many=True)
        return HttpResponse(json.dumps({'result_code':'0', 'data':sublocser.data}))
    else:
        return HttpResponse(json.dumps({'result_code':'1'}))



@api_view(['GET', 'POST'])
def submitDistance(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id','1')
        assign_id = request.POST.get('assign_id','1')
        distance = request.POST.get('distance','0')
        assigns = AreaAssign.objects.filter(id=assign_id, member_id=member_id)
        if assigns.count() > 0:
            assign = assigns[0]
            assign.client_dist = distance
            assign.save()
            resp = {'result_code':'0'}
            return HttpResponse(json.dumps(resp))
        else:
            resp = {'result_code':'1'}
            return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def getMyCumulativeDistance(request):
    member_id = request.GET['member_id']
    routes = Route.objects.filter(member_id=member_id, status='reported')
    cumulative = 0
    for route in routes:
        cumulative = cumulative + float(route.distance)

    return HttpResponse(json.dumps({'result_code':'0', 'cumulative':str(cumulative)}))































###################################################################################### Admin ##################################################################################################################################

def get_GET_info(url):
    response = requests.get(url)
    return response.json()

def index(request):
    return redirect('/rakubaru/rahome')


@api_view(['GET', 'POST'])
def ralogin(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')

        members = Rmember.objects.filter(email=settings.RAKUBARU_ADMIN_EMAIL, role='admin')
        # members = Rmember.objects.filter(email=email, role='admin')
        # if members.count() == 0:
        #     member = Rmember()
        #     member.admin_id = '0'
        #     member.name = name
        #     member.email = email
        #     member.password = 'admin'
        #     member.role = 'admin'
        #     member.registered_time = str(int(round(time.time() * 1000)))
        #     member.save()
        #     request.session['adminID'] = member.pk
        #     return redirect('/rakubaru/rahome')
        if members.count() > 0:
            member = members[0]
            request.session['adminID'] = member.pk
            return redirect('/rakubaru/rahome')
        else:
            return render(request, 'rakubaru/result.html',
                          {'response': 'Eメールまたはパスワードが間違っています。'})



@api_view(['GET', 'POST'])
def rasublogin(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        members = Rmember.objects.filter(email=email, password=password, role='admin')
        if members.count() > 0:
            member = members[0]
            request.session['adminID'] = member.pk
            return redirect('/rakubaru/rahome')
        else:
            return render(request, 'rakubaru/result.html',
                          {'response': 'Eメールまたはパスワードが間違っています。'})


def rasignuppage(request):
    return render(request, 'rakubaru/signup.html')


def rasignup(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        members = Rmember.objects.filter(email=email, role='admin')
        count = members.count()
        if count ==0:
            member = Rmember()
            member.admin_id = '0'
            member.name = name
            member.email = email
            member.password = password
            member.role = 'admin'
            member.save()

            request.session['adminID'] = member.pk

            # title = 'Approval To A New EverGoal Administrator'
            # subject = member.name + ' signed up as a new administrator'
            # message = 'Hello Florian Gedeon, I signed up with EverGoal admin site as a new administrator.<br>I will be very happy if you kindly activate my account so I could invite my employees to EverGoal.<br><br>'
            # message = message + '<a href="https://floriangedeon.eu.pythonanywhere.com/eaapproveadmin?member_id=' + str(member.pk) + '" target="_blank" style="font-size:18px; color:blue;">Activate</a><br><br>'
            # message = message + '<a href="https://floriangedeon.eu.pythonanywhere.com/eaadmins?member_id=' + str(member.pk) + '" target="_blank" style="font-size:14px; color:blue;">Please visit your admin site to see my account</a><br>'
            # message = message + 'Best Regards<br>' + member.name

            # from_email = member.email
            # to_emails = []
            # to_emails.append(settings.RAKUBARU_ADMIN_EMAIL)
            # send_mail_message(from_email, to_emails, title, subject, message)

            return redirect('/rakubaru/rahome')

        else:
            return render(request, 'rakubaru/result.html',
                          {'response': 'このアカウントはすでに存在します。 ログインしてください。'})

def raforgotpasswordpage(request):
    return render(request, 'rakubaru/forgot_password.html')



@api_view(['GET', 'POST'])
def raforgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        members = Rmember.objects.filter(email=email, role='admin')
        if members.count() == 0:
            return render(request, 'rakubaru/result.html',
                          {'response': 'このメールは存在しません。 別のものを試してください。'})

        message = 'こんにちは、<br><br>以下のリンクをクリックして、らくばるポスティング管理パネルのパスワードをリセットしてください。<br><br><a href=\'' + settings.URL + '/rakubaru/raresetpassword?email=' + email
        message = message + '\' target=\'_blank\'>' + 'パスワードをリセットするには、このリンクをクリックしてください' + '</a><br><br>'
        message = message + '※このメールは送信専用のため、返信はできません。<br><br>らくばるポスティング チーム'

        html =  """\
                    <html>
                        <head></head>
                        <body>
                            <h2 style="color:#02839a;">らくばるポスティング管理者のセキュリティ更新情報</h2>
                            <div style="font-size:14px; word-break: break-all; word-wrap: break-word;">
                                {mes}
                            </div>
                        </body>
                    </html>
                """
        html = html.format(mes=message)

        ###     <a href="#"><img src="https://www.rakubaru-posting.com/static/images/rakubaru/appicon.jpg" style="width:120px; height:120px; border-radius:10px; margin-left:25px;"/></a>

        # admins = Rmember.objects.filter(role='admin')
        fromEmail = settings.RAKUBARU_ADMIN_EMAIL
        # if admins.count() > 0:
        #     admin = admins[0]
        #     fromEmail = admin.email
        toEmailList = []
        toEmailList.append(email)
        msg = EmailMultiAlternatives('パスワードのリセットを許可しました', '', fromEmail, toEmailList)
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)

        return render(request, 'rakubaru/result.html',
                          {'response': 'メールにメッセージを送信しました。 パスワードを確認してリセットしてください。'})


def raresetpassword(request):
    email = request.GET['email']
    members = Rmember.objects.filter(email=email, role='admin')
    member = members[0]
    return render(request, 'rakubaru/resetpwd.html', {'member':member})



def rahome(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    members = Rmember.objects.filter(admin_id=adminID).order_by('-id')
    for member in members:
        dist = 0
        routes = Route.objects.filter(member_id=member.pk, status='reported')
        for route in routes:
            if route.distance is not None:
                dist = dist + float(route.distance)
        member.cumulative_distance = str(round(float(dist), 3))

    return render(request, 'rakubaru/home.html', {'members':members, 'me':me})



def ralogout(request):
    request.session['adminID'] = 0
    return redirect('/rakubaru/')


@api_view(['GET', 'POST'])
def ranewemployee(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    if request.method == 'POST':

        name = request.POST.get('name', '')
        eml = request.POST.get('email', '')
        phone = request.POST.get('phone', '')

        users = Rmember.objects.filter(email=eml)
        count = users.count()
        if count == 0:
            member = Rmember()
            member.admin_id = str(me.pk)
            member.name = name
            member.email = eml
            member.password = generateRandomPassword(10)
            member.phone_number = phone
            member.picture_url = settings.URL + '/static/images/rakubaru/profile.png'
            member.registered_time = str(int(round(time.time() * 1000)))
            member.save()

            fs = FileSystemStorage()

            try:
                f = request.FILES['picture']
                filename = fs.save(f.name, f)
                uploaded_url = fs.url(filename)
                member.picture_url = settings.URL + uploaded_url
                member.save()
            except MultiValueDictKeyError:
                print('No exists')

            title = 'らくばるへようこそ'
            subject = 'らくばるへの招待'
            message = 'こんにちは ' + member.name + 'さん,<br><br>あなたはらくばるアプリに招待されています。<br>'
            message = message + '初めてアプリを開いてサインアップするときに、次の認証情報を使用してアプリにログインできます。<br><br>'
            message = message + 'パスワード： ' + member.password + '<br><br>'
            message = message + 'ここでアプリをダウンロードできます： <br>'
            message = message + '<a href="https://play.google.com/store/apps/details?id=com.app.rakubaru"><img src="https://www.rakubaru-posting.com/static/images/rakubaru/playstore.png" style="width:150px;"></a>' + '<br>'
            message = message + '<a href="https://apps.apple.com/us/app/らくばるポスティング/id1543104404#?platform=iphone"><img src="https://www.rakubaru-posting.com/static/images/rakubaru/appstore.png" style="width:150px;"></a>' + '<br><br>'
            message = message + '※このメールは送信専用のため、返信はできません。<br><br>らくばるポスティング チーム'

            from_email = me.email
            to_emails = []
            to_emails.append(member.email)

            send_mail_message(from_email, to_emails, title, subject, message)

            return HttpResponse('success')

        else:
            return HttpResponse('existence')


def send_mail_message(from_email, to_emails, title, subject, message):
    html =  """\
                <html>
                    <head></head>
                    <body>

                        <h2 style="margin-left:10px; color:#02839a;">{title}</h2>
                        <div style="font-size:14px; white-space: pre-line; word-wrap: break-word;">
                            {mes}
                        </div>
                    </body>
                </html>
            """
    html = html.format(title=title, mes=message)

    msg = EmailMultiAlternatives(subject, '', from_email, to_emails)
    msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=False)


import random
import string

def generateRandomPassword(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str



def radelmember(request):
    member_id = request.GET['member_id']
    fs = FileSystemStorage()
    member = Rmember.objects.get(id=int(member_id))
    role = member.role
    if member.picture_url != '':
        fname = member.picture_url.replace(settings.URL + '/media/', '')
        fs.delete(fname)
    member.delete()

    routes = Route.objects.filter(member_id=member_id)
    for route in routes:
        points = Rpoint.objects.filter(route_id=route.pk)
        for pnt in points:
            pnt.delete()
        pins = Rpin.objects.filter(route_id=route.pk)
        for pin in pins:
            pin.delete()
        route.delete()

    devices = Device.objects.filter(member_id=member_id)
    devices.delete()

    if role == 'admin':
        emps = Rmember.objects.filter(admin_id=member_id)
        for emp in emps:
            routes = Route.objects.filter(member_id=emp.pk)
            for route in routes:
                points = Rpoint.objects.filter(route_id=route.pk)
                for pnt in points:
                    pnt.delete()
                pins = Rpin.objects.filter(route_id=route.pk)
                for pin in pins:
                    pin.delete()
                route.delete()
            devices = Device.objects.filter(member_id=emp.pk)
            devices.delete()

        paids = Paid.objects.filter(member_id=member_id)
        paids.delete()

        areas = Area.objects.filter(admin_id=member_id)
        for area in areas:
            sublocs = Sublocality.objects.filter(area_id=area.pk)
            sublocs.delete()
            assigns = AreaAssign.objects.filter(area_id=area.pk)
            assigns.delete()
            area.delete()

        return redirect('/superadmin')

    return redirect('/rakubaru/rahome')


def rapasswordchange(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    return  render(request, 'rakubaru/password_reset.html', {'me':me})


@api_view(['GET', 'POST'])
def rachangepassword(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    if request.method == 'POST':
        email = request.POST.get('email', '')
        oldpassword = request.POST.get('oldpassword', '')
        newpassword = request.POST.get('newpassword', '')

        if email == me.email and oldpassword == me.password:
            me.password = newpassword
            me.save()

        elif email == me.email and oldpassword != me.password:
            return render(request, 'rakubaru/result.html',
                          {'response': '古いパスワードが正しくありません。 正しいパスワードを入力してください'})

        else:
            members = Rmember.objects.filter(email=email)
            if members.count() > 0:
                return render(request, 'rakubaru/result.html',
                          {'response': '誰かがすでに同じメールを使用しています。 別のもので試してみてください'})
            me.email = email
            me.password = newpassword
            me.save()

        return redirect('/rakubaru/rahome')


def raallreports(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    routeList = []
    routes = Route.objects.filter(status='reported').order_by('-id')
    for route in routes:
        members = Rmember.objects.filter(admin_id=adminID, id=int(route.member_id))
        if members.count() > 0:
            # member = members[0]
            # route.name = member.name + '_' + datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%y%m%d_%H%M")
            routeList.append(route)

    reportList = getRouteListData(routeList)
    return render(request, 'rakubaru/reports.html', {'reports':reportList})


def getRouteListData(routes):
    import datetime
    reportList = []
    for route in routes:
        route.start_time = datetime.datetime.fromtimestamp(float(int(route.start_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.end_time = datetime.datetime.fromtimestamp(float(int(route.end_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.reported_time = datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%m/%d/%y %H:%M")
        route.speed = round(float(route.speed), 2)
        route.distance = round(float(route.distance), 3)
        con_sec, con_min, con_hour = convertMillis(int(route.duration))
        route.duration = "{0}h {1}m {2}s".format(str(int(con_hour)).zfill(2), str(int(con_min)).zfill(2), str(int(con_sec)).zfill(2))

        if float(route.distance) == 0:
            route.speed = '0.0'
            route.duration = '00h 00m 00s'

        members = Rmember.objects.filter(id=int(route.member_id))
        if members.count() > 0:
            member = members[0]
            data = {
                'member':member,
                'route':route,
            }
            reportList.append(data)
    return reportList



def convertMillis(millis):
     seconds=(millis/1000)%60
     minutes=(millis/(1000*60))%60
     hours=(millis/(1000*60*60))%24
     return seconds, minutes, hours

import math
def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier



def radelroute(request):
    route_id = request.GET['route_id']
    option = request.GET['option']
    route = Route.objects.get(id=int(route_id))
    points = Rpoint.objects.filter(route_id=route.pk)
    for pnt in points:
        pnt.delete()
    pins = Rpin.objects.filter(route_id=route.pk)
    for pin in pins:
        pin.delete()
    route.delete()

    if option == 'all':
        return redirect('/rakubaru/raallreports')
    elif option == 'user':
        member_id = request.GET['member_id']
        return redirect('/rakubaru/rauserreports?member_id=' + member_id)
    return redirect('/rakubaru/raallreports')


def rauserreports(request):
    import datetime
    member_id = request.GET['member_id']
    member = Rmember.objects.get(id=int(member_id))
    routes = Route.objects.filter(member_id=member.pk, status='reported').order_by('-id')
    # for route in routes:
    #     route.name = member.name + '_' + datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%y%m%d_%H%M")
    reportList = getRouteListData(routes)

    return render(request, 'rakubaru/reports.html', {'reports':reportList, 'member':member})


@api_view(['GET', 'POST'])
def rasearchreportbydate(request):
    if request.method == 'POST':
        key = request.POST.get('q', None)
        option = request.GET['option']

        try:
            if request.session['adminID'] == 0 or request.session['adminID'] == '':
                return render(request, 'rakubaru/admin.html')
        except KeyError:
            print('no session')
            return render(request, 'rakubaru/admin.html')

        adminID = request.session['adminID']
        me = Rmember.objects.get(id=adminID)

        if option == 'all':
            routes = Route.objects.all().order_by('-id')
            routeList = []
            for route in routes:
                members = Rmember.objects.filter(id=route.member_id)
                if members.count() > 0:
                    member = members[0]
                    if int(member.admin_id) == me.pk:
                        routeList.append(route)
            routeList = getroutessearchedbydate(routeList, key)
            return render(request, 'rakubaru/reports.html', {'reports':getRouteListData(routeList)})
        elif option == 'user':
            member_id = request.GET['member_id']
            member = Rmember.objects.get(id=int(member_id))
            routes = Route.objects.filter(member_id=member_id).order_by('-id')
            routeList = getroutessearchedbydate(routes, key)
            return render(request, 'rakubaru/reports.html', {'reports':getRouteListData(routeList), 'member':member})


def getroutessearchedbydate(routes, keyword):
    from datetime import datetime
    routeList = []
    for route in routes:
        if keyword.isdigit():
            keyDateObj = datetime.fromtimestamp(int(keyword)/1000)
            routeDateObj = datetime.fromtimestamp(int(route.reported_time)/1000)
            if keyDateObj.year == routeDateObj.year and keyDateObj.month == routeDateObj.month and keyDateObj.day == routeDateObj.day:
                routeList.append(route)
            else:
                routeDateObj = datetime.fromtimestamp(int(route.start_time)/1000)
                if keyDateObj.year == routeDateObj.year and keyDateObj.month == routeDateObj.month and keyDateObj.day == routeDateObj.day:
                    routeList.append(route)
                else:
                    routeDateObj = datetime.fromtimestamp(int(route.end_time)/1000)
                    if keyDateObj.year == routeDateObj.year and keyDateObj.month == routeDateObj.month and keyDateObj.day == routeDateObj.day:
                        routeList.append(route)

    return routeList


def raopenroutemap(request):
    import datetime
    route_id = request.GET['route_id']
    routes = Route.objects.filter(id=route_id)
    if routes.count() > 0:
        route = routes[0]
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
            route.duration = '00h 00m 00s'

        pnts = Rpoint.objects.filter(route_id=route.pk)
        pins = Rpin.objects.filter(member_id=route.member_id)
        for pin in pins:
            pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')

        data = {
            'route':route,
            'points':pnts,
            'pins':pins
        }

        return render(request, 'rakubaru/route.html', {'report':data})


def rapinmap(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)
    option = request.GET['option']
    if option == 'all':
        pinList = []
        pins = Rpin.objects.all()
        for pin in pins:
            members = Rmember.objects.filter(id=pin.member_id)
            if members.count() > 0:
                member = members[0]
                if int(member.admin_id) == me.pk:
                    pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')
                    pinList.append(pin)
        return render(request, 'rakubaru/pins.html', {'pins':pinList})
    elif option == 'user':
        member_id = request.GET['member_id']
        member = Rmember.objects.get(id=member_id)
        pins = Rpin.objects.filter(member_id=member_id)
        for pin in pins:
            pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')
        return render(request, 'rakubaru/pins.html', {'pins':pins, 'member':member})


@api_view(['GET', 'POST'])
def raeditroute(request):
    if request.method == 'POST':
        route_id = request.POST.get('route_id', '1')
        route_desc = request.POST.get('route_desc', '')
        routes = Route.objects.filter(id=route_id)
        if routes.count() > 0:
            route = routes[0]
            route.admin_desc = route_desc
            route.save()
            return HttpResponse('success')
        else:
            return HttpResponse('error')


@api_view(['GET', 'POST'])
def raemployeeprocess(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    if request.method == 'POST':

        member_id = request.POST.get('member_id', '1')
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        option = request.POST.get('option', '')

        users = Rmember.objects.filter(id=member_id)
        count = users.count()
        if count > 0:
            member = users[0]
            if option == 'reinvite':
                if member.status != '':
                    return HttpResponse('loggedin')
                title = 'らくばるへようこそ'
                subject = 'らくばるへの招待'
                message = 'こんにちは ' + member.name + 'さん,<br><br>あなたはらくばるアプリに招待されています。<br>'
                message = message + '初めてアプリを開いてサインアップするときに、次の認証情報を使用してアプリにログインできます。<br><br>'
                message = message + 'パスワード： ' + member.password + '<br><br>'
                message = message + 'ここでアプリをダウンロードできます： <br>'
                message = message + '<a href="https://play.google.com/store/apps/details?id=com.app.rakubaru"><img src="https://www.rakubaru-posting.com/static/images/rakubaru/playstore.png" style="width:150px;"></a>' + '<br>'
                message = message + '<a href="https://apps.apple.com/us/app/らくばるポスティング/id1543104404#?platform=iphone"><img src="https://www.rakubaru-posting.com/static/images/rakubaru/appstore.png" style="width:150px;"></a>' + '<br><br>'
                message = message + '※このメールは送信専用のため、返信はできません。<br><br>らくばるポスティング チーム'

                from_email = me.email
                to_emails = []
                to_emails.append(member.email)

                send_mail_message(from_email, to_emails, title, subject, message)

            elif option == 'profileedit':
                member.name = name
                member.phone_number = phone
                member.save()

            return HttpResponse('success')

        else:
            return HttpResponse('error')


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




def ratoplan(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    members = Rmember.objects.filter(admin_id=me.pk)
    if me.planned_members == '':
        me.planned_members = '1'
        me.save()
    count = members.count()
    ex_status = ''
    if count >= int(me.planned_members):
        ex_status = 'expired'

    paids = Paid.objects.filter(member_id=me.pk).order_by('-id')
    paid = paids[0]
    last_payment = paid.paid_amount

    if me.email == 'alertingjames@gmail.com' or me.email == 'yamamoto_h@nac-om.com':
        return render(request, 'rakubaru/payment_plans.html', {'me':me, 'status':ex_status, 'planned_count': int(me.planned_members), 'memb_count': count, 'last_payment':last_payment})
    else:
        return render(request, 'rakubaru/plans.html', {'me':me, 'status':ex_status, 'memb_count': count})



def ratopay(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    price = request.GET['price']
    plan = request.GET['plan']
    membs = request.GET['members']

    members = Rmember.objects.filter(admin_id=me.pk)
    if members.count() > int(membs):
        return render(request, 'rakubaru/result.html',
                                  {'response': '選択したプランの利用者上限が、現在の社員数を下回っています。登録社員を削除して選択しなおしてください。'})

    if int(price) == 0:
        me.plan = plan
        me.planned_members = membs
        me.pay_token = ''
        me.save()

        paid = Paid()
        paid.member_id = me.pk
        paid.plan = plan
        paid.paid_time = str(int(round(time.time() * 1000)))
        paid.save()

        return redirect('/rakubaru/ratoplan')

    response = get_GET_info('https://api.exchangeratesapi.io/latest?base=JPY')
    jsondata = json.dumps(response)
    ex_dict = json.loads(jsondata)

    # price = float(price) * float(ex_dict['rates']['USD']) * 100
    # price = float(price) * float(1/102.4051) * 100    ###### Stripe exchange rate: 102.4051
    price = float(price)

    return render(request, 'rakubaru/pay.html', {'price':price, 'me_id':me.pk, 'plan':plan, 'members':membs})


import stripe

@api_view(['GET', 'POST'])
def rapay(request):
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

        amount = int(float(price))
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="jpy",
                source=token  # obtained with Stripe.js
            )
            if charge is not None:
                paid = Paid()
                paid.member_id = me.pk
                paid.plan = plan
                paid.paid_time = str(int(round(time.time() * 1000)))
                paid.coupon_id = coupon_id
                paid.discount = discount
                paid.discount_amount = str(amount * float(discount) / 100)
                paid.paid_amount = str(amount - float(paid.discount_amount))
                paid.save()

                if me.planned_members == '':
                    me.planned_members = '1'

                me.planned_members = membs

                if plan == '5':
                    if me.plan == '4' or me.plan == '5':
                        me.planned_members = str(int(me.planned_members) + int(membs))
                    else:
                        me.planned_members = str(100 + int(membs))
                me.plan = plan
                me.pay_token = token
                me.save()

                return HttpResponse('success')

            else:
                return render(request, 'rakubaru/result.html',
                                  {'response': '支払いエラー。'})
        except stripe.error.InvalidRequestError as e:
            return render(request, 'rakubaru/result.html',
                                  {'response': str(e)})



@api_view(['GET', 'POST'])
def ratestpay(request):
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
                    me.subscriptionID = subscription.id
                    me.subperiodend = subscription.current_period_end
                    me.save()

                # return HttpResponse("subscription id: " + subscription.id)

                # charge = stripe.Charge.create(
                #     amount=amount,
                #     currency="jpy",
                #     source=token,  # obtained with Stripe.js
                #     description="Paid by " + email
                # )

                # if charge is not None:
                    paid = Paid()
                    paid.member_id = me.pk
                    paid.plan = plan
                    paid.paid_time = str(int(round(time.time() * 1000)))
                    paid.coupon_id = coupon_id
                    paid.discount = discount
                    paid.discount_amount = str(amount * float(discount) / 100)
                    paid.paid_amount = str(amount - float(paid.discount_amount))
                    paid.save()

                    if me.planned_members == '':
                        me.planned_members = '1'

                    me.planned_members = membs
                    me.plan = plan
                    me.save()

                    return HttpResponse('success')

                else:
                    return HttpResponse('支払いエラー。')

        except stripe.error.InvalidRequestError as e:
            return HttpResponse(str(e))





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



def toareas(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']

    areas = Area.objects.filter(admin_id=adminID).order_by('-id')
    areaList = []
    for area in areas:
        area.posted_time = datetime.datetime.fromtimestamp(float(int(area.posted_time)/1000)).strftime("%m/%d/%y %H:%M")
        sublocs = Sublocality.objects.filter(area_id=area.pk)
        data = {
            'area': area,
            'sublocs': sublocs
        }
        areaList.append(data)
    members = Rmember.objects.filter(admin_id=adminID).order_by('-id')
    memberList = []
    for member in members:
        if member.registered_time != '':
            member.registered_time = datetime.datetime.fromtimestamp(float(int(member.registered_time)/1000)).strftime("%m/%d/%y %H:%M")
            memberList.append(member)

    context = {'areas':areaList, 'members':memberList}
    try:
        area_id = request.GET['area_id']
        area = Area.objects.get(id=area_id)
        context = {'areas':areaList, 'members':memberList, 'area':area}
    except KeyError:
        print('No key')
    return render(request, 'rakubaru/arealist.html', context)


@api_view(['GET', 'POST'])
def delarea(request):
    area_id = request.GET['area_id']
    area = Area.objects.get(id=area_id)
    if area is None:
        return HttpResponse({'result':'no_exist'})
    area.delete()
    sublocs = Sublocality.objects.filter(area_id=area_id)
    sublocs.delete()
    assigns = AreaAssign.objects.filter(area_id=area_id)
    assigns.delete()
    return HttpResponse(json.dumps({'result':'success'}))


def areasetup(request):
    return render(request, 'rakubaru/area_setup.html')

def editarea(request):
    area_id = request.GET['area_id']
    area = Area.objects.get(id=area_id)
    if area is None:
        return redirect('/rakubaru/toareas')
    sublocs = Sublocality.objects.filter(area_id=area.pk)
    for subloc in sublocs:
        subloc.locarr = subloc.locarr.replace("'","")
    context = {
        'area': area,
        'sublocs': sublocs
    }
    return render(request, 'rakubaru/edit_area.html', context)


@api_view(['GET', 'POST'])
def postarea(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']

    if request.method == 'POST':
        area_name = request.POST.get('area_name', '')
        copies = request.POST.get('copies', '0')
        unit_price = request.POST.get('unit_price', '0')
        allowance = request.POST.get('allowance', '0')
        amount = request.POST.get('amount', '0')
        distance = request.POST.get('distance', '0')
        locarr = request.POST.get('locarr', '')

        sublocs = request.POST.get('sublocalities', '')

        area = Area()
        area.admin_id = adminID
        area.area_name = area_name
        area.copies = copies
        area.unit_price = unit_price
        area.allowance = allowance
        area.amount = amount
        area.distance = distance
        area.client_dist = '0'
        area.clients = '0'
        area.locarr = locarr
        area.posted_time = str(int(round(time.time() * 1000)))

        area.save()

        if sublocs != '':
            try:
                decoded = json.loads(sublocs)
                for data in decoded['sublocalities']:

                    lat = data['lat']
                    lng = data['lng']
                    loc_name = data['loc_name']
                    color = data['color']
                    locarr = data['locarr']

                    subloc = Sublocality()
                    subloc.area_id = area.pk
                    subloc.loc_name = loc_name
                    subloc.lat = lat
                    subloc.lng = lng
                    subloc.color = color
                    subloc.locarr = locarr
                    subloc.save()

            except:
                print('Subloc data saving error')
                resp = {'result': 'error'}
                return HttpResponse(json.dumps(resp))

        resp = {'result': 'success'}
        return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def assignarea(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']

    if request.method == 'POST':
        area_id = request.POST.get('area_id', '0')
        title = request.POST.get('title', '')
        customer = request.POST.get('customer', '')
        copies = request.POST.get('copies', '0')
        unit_price = request.POST.get('unit_price', '0')
        allowance = request.POST.get('allowance', '0')
        amount = request.POST.get('amount', '0')
        distance = request.POST.get('distance', '0')
        distribution = request.POST.get('distribution', '')
        start_time = request.POST.get('start_time', '0')
        end_time = request.POST.get('end_time', '0')

        ids = request.POST.getlist('users[]')

        i = 0
        for member_id in ids:
            assigns = AreaAssign.objects.filter(member_id=member_id, area_id=area_id, distribution=distribution, start_time=start_time, end_time=end_time)
            if assigns.count() > 0:
                continue
            i = i + 1
            assign = AreaAssign()
            assign.admin_id = adminID
            assign.area_id = area_id
            assign.member_id = member_id
            assign.title = title
            assign.customer = customer
            assign.copies = copies
            assign.unit_price = unit_price
            assign.allowance = allowance
            assign.amount = amount
            assign.distance = distance
            assign.distribution = distribution
            assign.start_time = start_time
            assign.end_time = end_time
            assign.client_dist = '0'
            assign.assigned_time = str(int(round(time.time() * 1000)))
            assign.save()

        areas = Area.objects.filter(id=area_id)
        if areas.count() > 0:
            area = areas[0]
            area.clients = str(int(area.clients) + i)
            area.save()

        return HttpResponse(json.dumps({'result':'success'}))


@api_view(['GET', 'POST'])
def getallassigns(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']

    assigns = []
    forArea = None
    try:
        area_id = request.GET['area_id']
        assigns = AreaAssign.objects.filter(admin_id=adminID, area_id=area_id).order_by('-id')
        ar = Area.objects.get(id=area_id)
        forArea = ar
    except KeyError:
        assigns = AreaAssign.objects.filter(admin_id=adminID).order_by('-id')
    assignList = []
    for assign in assigns:
        areas = Area.objects.filter(id=assign.area_id)
        if areas.count() > 0:
            area = areas[0]
            members = Rmember.objects.filter(id=assign.member_id)
            if members.count() > 0:
                member = members[0]
                routes = Route.objects.filter(member_id=member.pk, assign_id=assign.pk, status='reported')
                works = routes.count()
                distance = 0
                for route in routes:
                    distance = distance + float(route.distance)
                assigned_distance = area.distance
                progress = round(float(distance * 100 / float(assigned_distance)), 2)
                data = {
                    'assign': assign,
                    'area': area,
                    'member': member,
                    'progress':progress,
                    'works':works,
                    'dist_start':datetime.datetime.fromtimestamp(float(int(assign.start_time)/1000)).strftime("%m/%d/%y"),
                    'dist_end':datetime.datetime.fromtimestamp(float(int(assign.end_time)/1000)).strftime("%m/%d/%y"),
                    'assigned':datetime.datetime.fromtimestamp(float(int(assign.assigned_time)/1000)).strftime("%m/%d/%y %H:%M")
                }
                assignList.append(data)

    context = {'assigns':assignList, 'area':forArea}
    try:
        assign_id = request.GET['assign_id']
        context = {'assigns':assignList, 'area':forArea, 'assign_id':assign_id}
    except KeyError:
        print('No key')
    return render(request, 'rakubaru/assignlist.html', context)



def assignedworks(request):
    assign_id = request.GET['assign_id']
    member_id = request.GET['member_id']
    assign = AreaAssign.objects.get(id=assign_id)
    routes = Route.objects.filter(member_id=member_id, assign_id=assign_id, status='reported').order_by('-id')
    reportList = getRouteListData(routes)
    return render(request, 'rakubaru/assigned_works.html', {'assign':assign, 'reports':reportList})


def tomember(request):
    member_id = request.GET['member_id']
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    me = Rmember.objects.get(id=adminID)

    members = Rmember.objects.filter(admin_id=adminID).order_by('-id')
    member = Rmember.objects.get(id=member_id)

    return render(request, 'rakubaru/home.html', {'members':members, 'me':me, 'member':member})



@api_view(['GET', 'POST'])
def updatearea(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']

    if request.method == 'POST':
        area_id = request.POST.get('area_id', '0')
        area_name = request.POST.get('area_name', '')
        copies = request.POST.get('copies', '0')
        unit_price = request.POST.get('unit_price', '0')
        allowance = request.POST.get('allowance', '0')
        amount = request.POST.get('amount', '0')
        distance = request.POST.get('distance', '0')
        locarr = request.POST.get('locarr', '')

        sublocs = request.POST.get('sublocalities', '')

        area = Area.objects.get(id=area_id)
        area.area_name = area_name
        area.copies = copies
        area.unit_price = unit_price
        area.allowance = allowance
        area.amount = amount
        area.distance = distance
        area.locarr = locarr

        area.save()

        if sublocs != '':
            sls = Sublocality.objects.filter(area_id=area_id)
            sls.delete()
            try:
                decoded = json.loads(sublocs)
                for data in decoded['sublocalities']:

                    lat = data['lat']
                    lng = data['lng']
                    loc_name = data['loc_name']
                    color = data['color']
                    locarr = data['locarr']

                    subloc = Sublocality()
                    subloc.area_id = area.pk
                    subloc.loc_name = loc_name
                    subloc.lat = lat
                    subloc.lng = lng
                    subloc.color = color
                    subloc.locarr = locarr
                    subloc.save()

            except:
                print('Subloc data saving error')
                resp = {'result': 'error'}
                return HttpResponse(json.dumps(resp))

        resp = {'result': 'success'}
        return HttpResponse(json.dumps(resp))



@api_view(['GET', 'POST'])
def editassign(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']

    if request.method == 'POST':
        assign_id = request.POST.get('assign_id', '0')
        title = request.POST.get('title', '')
        customer = request.POST.get('customer', '')
        copies = request.POST.get('copies', '0')
        unit_price = request.POST.get('unit_price', '0')
        allowance = request.POST.get('allowance', '0')
        amount = request.POST.get('amount', '0')
        distance = request.POST.get('distance', '0')
        distribution = request.POST.get('distribution', '')
        start_time = request.POST.get('start_time', '0')
        end_time = request.POST.get('end_time', '0')

        assign = AreaAssign.objects.get(id=assign_id)
        if assign is None:
            return HttpResponse(json.dumps({'result':'no_exist'}))
        assign.title = title
        assign.customer = customer
        assign.copies = copies
        assign.unit_price = unit_price
        assign.allowance = allowance
        assign.amount = amount
        assign.distance = distance
        assign.distribution = distribution
        assign.start_time = start_time
        assign.end_time = end_time
        assign.save()

        return HttpResponse(json.dumps({'result':'success'}))



@api_view(['GET', 'POST'])
def delassign(request):
    assign_id = request.GET['assign_id']
    assign = AreaAssign.objects.get(id=assign_id)
    area_id = assign.area_id
    if assign is None:
        return HttpResponse({'result':'no_exist'})
    assign.delete()
    areas = Area.objects.filter(id=area_id)
    if areas.count() > 0:
        area = areas[0]
        if int(area.clients) > 0:
            area.clients = str(int(area.clients) - 1)
            area.save()
    return HttpResponse(json.dumps({'result':'success'}))


@api_view(['GET', 'POST'])
def searcharea(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    if request.method == 'POST':
        q = request.POST.get('q', '')
        areaList = []
        areas = Area.objects.filter(admin_id=adminID).order_by('-id')
        for area in areas:
            area.posted_time = datetime.datetime.fromtimestamp(float(int(area.posted_time)/1000)).strftime("%m/%d/%y %H:%M")
            sublocs = Sublocality.objects.filter(area_id=area.pk)
            data = {
                'area': area,
                'sublocs': sublocs
            }
            if q.lower() in area.area_name.lower():
                areaList.append(data)
            else:
                sublocs = Sublocality.objects.filter(area_id=area.pk)
                for subloc in sublocs:
                    if q.lower() in subloc.loc_name.lower():
                        areaList.append(data)
        members = Rmember.objects.filter(admin_id=adminID).order_by('-id')
        memberList = []
        for member in members:
            if member.registered_time != '':
                member.registered_time = datetime.datetime.fromtimestamp(float(int(member.registered_time)/1000)).strftime("%m/%d/%y %H:%M")
                memberList.append(member)

        context = {'areas':areaList, 'members':memberList}
        return render(request, 'rakubaru/arealist.html', context)

    elif request.method == 'GET':
        return redirect('/rakubaru/toareas')



@api_view(['GET', 'POST'])
def searchassign(request):
    import datetime
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']

    if request.method == 'POST':
        q = request.POST.get('q', '')

        assigns = AreaAssign.objects.filter(admin_id=adminID)
        assignList = []
        for assign in assigns:
            areas = Area.objects.filter(id=assign.area_id)
            if areas.count() > 0:
                area = areas[0]
                member = Rmember.objects.get(id=assign.member_id)
                data = {
                    'assign': assign,
                    'area': area,
                    'member': member,
                    'progress':30,
                    'works':1,
                    'dist_start':datetime.datetime.fromtimestamp(float(int(assign.start_time)/1000)).strftime("%m/%d/%y"),
                    'dist_end':datetime.datetime.fromtimestamp(float(int(assign.end_time)/1000)).strftime("%m/%d/%y"),
                    'assigned':datetime.datetime.fromtimestamp(float(int(assign.assigned_time)/1000)).strftime("%m/%d/%y %H:%M")
                }
                if q.lower() in assign.title.lower():
                    assignList.append(data)
                elif q.lower() in assign.distribution.lower():
                    assignList.append(data)
                elif q.lower() in member.name.lower():
                    assignList.append(data)
                elif q.lower() in area.area_name.lower():
                    assignList.append(data)
                else:
                    sublocs = Sublocality.objects.filter(area_id=area.pk)
                    for subloc in sublocs:
                        if q.lower() in subloc.loc_name.lower():
                            assignList.append(data)

        context = {'assigns':assignList}
        return render(request, 'rakubaru/assignlist.html', context)

    elif request.method == 'GET':
        return redirect('/rakubaru/getallassigns')


@api_view(['GET', 'POST'])
def schassignbydate(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']

    if request.method == 'POST':
        q = request.POST.get('q', '')

        assigns = AreaAssign.objects.filter(admin_id=adminID)
        assignList = []
        for assign in assigns:
            areas = Area.objects.filter(id=assign.area_id)
            if areas.count() > 0:
                area = areas[0]
                member = Rmember.objects.get(id=assign.member_id)
                import datetime
                data = {
                    'assign': assign,
                    'area': area,
                    'member': member,
                    'progress':30,
                    'works':1,
                    'dist_start':datetime.datetime.fromtimestamp(float(int(assign.start_time)/1000)).strftime("%m/%d/%y"),
                    'dist_end':datetime.datetime.fromtimestamp(float(int(assign.end_time)/1000)).strftime("%m/%d/%y"),
                    'assigned':datetime.datetime.fromtimestamp(float(int(assign.assigned_time)/1000)).strftime("%m/%d/%y %H:%M")
                }

                from datetime import datetime

                if q.isdigit():
                    keydateObj = datetime.fromtimestamp(int(q)/1000)
                    startdateObj = datetime.fromtimestamp(int(assign.start_time)/1000)
                    enddateObj = datetime.fromtimestamp(int(assign.end_time)/1000)
                    assigneddateObj = datetime.fromtimestamp(int(assign.assigned_time)/1000)
                    if keydateObj.year == startdateObj.year and keydateObj.month == startdateObj.month and keydateObj.day == startdateObj.day:
                        assignList.append(data)
                    elif keydateObj.year == enddateObj.year and keydateObj.month == enddateObj.month and keydateObj.day == enddateObj.day:
                        assignList.append(data)
                    elif keydateObj.year == assigneddateObj.year and keydateObj.month == assigneddateObj.month and keydateObj.day == assigneddateObj.day:
                        assignList.append(data)

        context = {'assigns':assignList}
        return render(request, 'rakubaru/assignlist.html', context)

    elif request.method == 'GET':
        return redirect('/rakubaru/getallassigns')


def broadcast(request):
    try:
        if request.session['adminID'] == 0 or request.session['adminID'] == '':
            return render(request, 'rakubaru/admin.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/admin.html')

    adminID = request.session['adminID']
    admin = Rmember.objects.get(id=adminID)

    if request.method == 'POST':
        message = request.POST.get('broadmessage', '')

        members = Rmember.objects.filter(admin_id=adminID)

        for member in members:
            title = 'らくばる 管理者から'
            subject = 'らくばる 管理者から'

            from_email = admin.email
            to_emails = []
            to_emails.append(member.email)
            send_mail_message(from_email, to_emails, title, subject, message)

        return HttpResponse('success')





























































############################################################################################# Super Admin ##############################################################################################

def superadmin(request):
    try:
        if request.session['superAdminID'] == 0 or request.session['superAdminID'] == '':
            return render(request, 'rakubaru/login.html')
    except KeyError:
        print('no session')
        return render(request, 'rakubaru/login.html')

    superAdminID = request.session['superAdminID']
    me = Rmember.objects.get(id=superAdminID)

    admins = Rmember.objects.filter(role='admin').order_by('-id')
    adminList = []
    for admin in admins:
        if admin.pk == 1 or admin.pk == 4 or admin.pk == 14: continue
        members = Rmember.objects.filter(admin_id=admin.pk, status='loggedin')
        admin.plan = getplan(admin.plan)
        data = {
            'admin': admin,
            'employees': members.count()
        }
        if admin.pk != 1:
            adminList.append(data)

    return render(request, 'rakubaru/superhome.html', {'admins':adminList, 'me':me})


def getplan(plan):
    pln = ''
    if plan == '' or plan == '0':
        pln = '無料'
    elif plan == '1':
        pln = '5,000円'
    elif plan == '2':
        pln = '14,000円'
    elif plan == '3':
        pln = '23,000円'
    elif plan == '4':
        pln = '45,000円'
    elif plan == '5':
        pln = '45,000+円'

    return pln


@api_view(['POST', 'GET'])
def superlogin(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        # members = Rmember.objects.filter(email=email, id=1)
        members = Rmember.objects.filter(id=1)
        if members.count() > 0:
            superadmin = members[0]
            request.session['superAdminID'] = superadmin.pk

            return redirect('/superadmin')
        else:
            return render(request, 'rakubaru/result.html',
                          {'response': 'Eメールまたはパスワードが間違っています。'})



def employees(request):
    admin_id = request.GET['admin_id']
    admin = Rmember.objects.get(id=admin_id)
    members = Rmember.objects.filter(admin_id=admin.pk, status='loggedin').order_by('-id')

    return render(request, 'rakubaru/employees.html', {'members':members, 'admin':admin})


def emreports(request):
    import datetime
    member_id = request.GET['member_id']
    member = Rmember.objects.get(id=int(member_id))
    routes = Route.objects.filter(member_id=member.pk, status='reported').order_by('-id')
    reportList = getRouteListData(routes)

    return render(request, 'rakubaru/emreports.html', {'reports':reportList, 'member':member})


def adminreports(request):
    admin_id = request.GET['admin_id']
    admin = Rmember.objects.get(id=int(admin_id))
    routeList = []
    routes = Route.objects.filter(status='reported').order_by('-id')
    for route in routes:
        members = Rmember.objects.filter(admin_id=admin.pk, id=int(route.member_id))
        if members.count() > 0:
            # member = members[0]
            # route.name = member.name + '_' + datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%y%m%d_%H%M")
            routeList.append(route)

    reportList = getRouteListData(routeList)
    return render(request, 'rakubaru/emreports.html', {'reports':reportList, 'admin':admin})


def allreports(request):
    routeList = []
    routes = Route.objects.filter(status='reported').order_by('-id')
    for route in routes:
        members = Rmember.objects.filter(id=int(route.member_id))
        if members.count() > 0:
            # member = members[0]
            # route.name = member.name + '_' + datetime.datetime.fromtimestamp(float(int(route.reported_time)/1000)).strftime("%y%m%d_%H%M")
            routeList.append(route)

    reportList = getRouteListData(routeList)
    return render(request, 'rakubaru/emreports.html', {'reports':reportList})


def emroutemap(request):
    import datetime
    route_id = request.GET['route_id']
    routes = Route.objects.filter(id=route_id)
    if routes.count() > 0:
        route = routes[0]
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
            route.duration = '00h 00m 00s'

        pnts = Rpoint.objects.filter(route_id=route.pk)
        pins = Rpin.objects.filter(member_id=route.member_id)
        for pin in pins:
            pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')

        data = {
            'route':route,
            'points':pnts,
            'pins':pins
        }

        return render(request, 'rakubaru/route.html', {'report':data})



def empinmap(request):
    import datetime
    option = request.GET['option']
    if option == 'all':
        pinList = []
        pins = Rpin.objects.all()
        for pin in pins:
            members = Rmember.objects.filter(id=pin.member_id)
            if members.count() > 0:
                member = members[0]
                pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')
                pinList.append(pin)
        return render(request, 'rakubaru/pins.html', {'pins':pinList})
    elif option == 'admin':
        admin_id = request.GET['admin_id']
        pinList = []
        pins = Rpin.objects.all()
        for pin in pins:
            members = Rmember.objects.filter(id=pin.member_id)
            if members.count() > 0:
                member = members[0]
                if int(member.admin_id) == int(admin_id):
                    pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')
                    pinList.append(pin)
        return render(request, 'rakubaru/pins.html', {'pins':pinList})
    elif option == 'user':
        member_id = request.GET['member_id']
        member = Rmember.objects.get(id=member_id)
        pins = Rpin.objects.filter(member_id=member_id)
        for pin in pins:
            pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')
        return render(request, 'rakubaru/pins.html', {'pins':pins, 'member':member})


def superlogout(request):
    request.session['superAdminID'] = 0
    return redirect('/superadmin/')



def allpayments(request):
    import datetime
    allpaids = Paid.objects.all().order_by('-id')
    paymentList = []
    for paid in allpaids:
        paid_time = datetime.datetime.fromtimestamp(float(int(paid.paid_time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')
        paid_month = datetime.datetime.fromtimestamp(float(int(paid.paid_time)/1000)).strftime("%m")
        paids = Paid.objects.filter(member_id=paid.member_id)
        if paids.count() > 0:
            lastpaid = paids[0]
            for pd in paids:
                if int(pd.paid_time) < int(paid.paid_time) and int(pd.paid_time) >= int(lastpaid.paid_time):
                    lastpaid = pd
            if lastpaid.pk == paid.pk:
                paid.paid_time = 'アップグレード: ' + paid_time
            elif int(paid.paid_time) > int(lastpaid.paid_time):
                if paid.plan == '': paid.plan = '0'
                if lastpaid.plan == '': lastpaid.plan = '0'
                if int(paid.plan) > int(lastpaid.plan): paid.paid_time = 'アップグレード: ' + paid_time
                else: paid.paid_time = 'ダウングレード: ' + paid_time
            else:
                paid.paid_time = 'アップグレード: ' + paid_time
        paid.plan = getplan(paid.plan)
        members = Rmember.objects.filter(id=paid.member_id)
        if members.count() > 0:
            member = members[0]
            if member.planned_members == '': member.planned_members = '0'
            data = {
                'payment':paid,
                'member':member,
                'month':paid_month
            }
            paymentList.append(data)

    return render(request, 'rakubaru/payments.html', {'payments':paymentList})



def openlanding(request):
    return render(request, 'rakubaru/landing.html')






def test(request):
    import datetime
    route_id = request.GET['route_id']
    routes = Route.objects.filter(id=route_id)
    if routes.count() > 0:
        route = routes[0]
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
            route.duration = '00h 00m 00s'

        pnts = Rpoint.objects.filter(route_id=route.pk)
        pins = Rpin.objects.filter(member_id=route.member_id)
        for pin in pins:
            pin.time = datetime.datetime.fromtimestamp(float(int(pin.time)/1000)).strftime("%m/%d/%y %r").replace('AM', '午前').replace('PM', '午後')

        data = {
            'route':route,
            'points':pnts,
            'pins':pins
        }

        return render(request, 'rakubaru/route_anim.html', {'report':data})



def couponpage(request):
    coupons  = Coupon.objects.all().order_by('-id')
    for coupon in coupons:
        current = int(round(time.time() * 1000))
        if current > int(coupon.expire_time):
            coupon.status = 'expired'
    return render(request, 'rakubaru/coupon.html', {'coupons':coupons})



@api_view(['GET', 'POST'])
def createCoupon(request):
    if request.method == 'POST':
        discount = request.POST.get('discount', '0')
        months = request.POST.get('month', '0')
        days = request.POST.get('day', '0')
        hours = request.POST.get('hour', '0')

        if int(discount) == 0: return render(request, 'rakubaru/result.html', {'response': '割引値は0であってはなりません。割引値を入力してください。'})

        coupon = Coupon()
        coupon.code = generateCouponCode(8)
        coupon.discount = discount
        lifespanMilisecs = (int(months) * 30 * 86400 + int(days) * 86400 + int(hours) * 3600) * 1000
        if lifespanMilisecs == 0:
            coupon.expire_time = '1000000000000000'
        else: coupon.expire_time = str(int(round(time.time() * 1000)) + lifespanMilisecs)
        coupon.save()

        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY

        prices = Price.objects.filter(price=int(5000*(1 - int(discount)/100)))
        if prices.count() == 0:
            products = Product.objects.all()
            if products.count() > 0:
                product = products[0]
                price = stripe.Price.create(
                  nickname='Standard Monthly',
                  product=product.productID,
                  unit_amount=int(5000*(1 - int(discount)/100)),
                  currency='jpy',
                  recurring={
                    'interval': 'month',
                    'usage_type': 'licensed',
                  },
                )
                if price is not None:
                    prc = Price()
                    prc.product_id = product.pk
                    prc.price = str(int(5000*(1 - int(discount)/100)))
                    prc.priceID = price.id
                    prc.save()

        return redirect('/couponpage')

def delcoupon(request):
    coupon_id = request.GET['coupon_id']
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.delete()
    return redirect('/couponpage')


def generateCouponCode(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str



@api_view(['POST', 'GET'])
def checkcoupon(request):
    code = request.GET['coupon_code']
    coupons = Coupon.objects.filter(code=code)
    if coupons.count() > 0:
        coupon = coupons[0]
        discount = coupon.discount
        current = int(round(time.time() * 1000))
        remaining = int(coupon.expire_time) - current
        if remaining >= 0:
            return HttpResponse(json.dumps({'status':'0', 'coupon_id':str(coupon.pk), 'discount':str(discount)}))
        else:
            return HttpResponse(json.dumps({'status':'1', 'coupon_id':str(coupon.pk), 'discount':str(discount)}))
    else:
        return HttpResponse(json.dumps({'status':'2'}))



def monthcouponhistorydata(request):
    from datetime import datetime

    current = int(round(time.time() * 1000))
    currentObj = datetime.fromtimestamp(current/1000)

    coupons  = Coupon.objects.all()
    couponList = []
    for coupon in coupons:
        current = int(round(time.time() * 1000))
        if current > int(coupon.expire_time):
            coupon.status = 'expired'
        paids = Paid.objects.filter(coupon_id=coupon.pk)
        disvalList = []
        for month in range(1, 13):
            i = 0
            for paid in paids:
                paidObj = datetime.fromtimestamp(int(paid.paid_time)/1000)
                if currentObj.year == paidObj.year and month == paidObj.month:
                    i = i + float(paid.discount_amount)
            disvalList.append(i)

        j = 0
        for paid in paids:
            paidObj = datetime.fromtimestamp(int(paid.paid_time)/1000)
            if paidObj.year == currentObj.year - 1 and paidObj.month == 12:
                j = j + float(paid.discount_amount)
        disvalList.insert(0, j)

        data = {
            'coupon': coupon,
            'monthdiscountlist': disvalList
        }
        couponList.append(data)

    return render(request, 'rakubaru/coupon_history.html', {'coupons':couponList})




from background_task import background
@background(schedule=5)
def run_task():
    from datetime import datetime
    import calendar

    print(str(int(round(time.time() * 1000))))

    current = int(round(time.time() * 1000))
    currentObj = datetime.fromtimestamp(current/1000)

    admins = Rmember.objects.filter(role='admin')
    for admin in admins:
        pds = Paid.objects.filter(member_id=admin.pk)
        if pds.count() > 0:
            pd = pds[pds.count() - 1]
            if int(pd.plan) > 0:
                lastPaidTimeObj = datetime.fromtimestamp(int(pd.paid_time)/1000)
                thismonthdays = calendar.monthrange(currentObj.year,currentObj.month)[1]
                if currentObj.month != lastPaidTimeObj.month and lastPaidTimeObj.day > thismonthdays and currentObj.day == thismonthdays:
                    monthlypay(admin, pd)
                elif currentObj.month != lastPaidTimeObj.month and lastPaidTimeObj.day == currentObj.day:
                    monthlypay(admin, pd)


def monthlypay(admin, pd):
    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY

    price = pd.paid_amount
    plan = pd.plan
    coupon_id = pd.coupon_id
    discount = pd.discount
    token = admin.pay_token
    amount = int(float(price))

    if token == '':
        send_mail_message(settings.RAKUBARU_ADMIN_EMAIL, [admin.email], '新しい月の支払いに失敗しました。', '新しい月の支払いに失敗しました。', '新しい月の支払いに失敗しました。お支払いカードを接続してお支払いください。<br><br>らくばるポスティング チーム')
        return

    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency="jpy",
            source=token  # obtained with Stripe.js
        )
        if charge is not None:
            paid = Paid()
            paid.member_id = admin.pk
            paid.plan = plan
            paid.paid_amount = price
            paid.paid_time = str(int(round(time.time() * 1000)))
            paid.coupon_id = coupon_id
            paid.discount = discount
            paid.discount_amount = pd.discount_amount
            paid.save()

            print('paid')

        else:
            send_mail_message(settings.RAKUBARU_ADMIN_EMAIL, [admin.email], '新しい月の支払いに失敗しました。', '新しい月の支払いに失敗しました。', '新しい月の支払いに失敗しました。お支払いカードを確認して、もう一度お試しください。<br><br>らくばるポスティング チーム')

    except stripe.error.InvalidRequestError as e:
        print(str(e))






















# def deltestadmins(request):
#     fs = FileSystemStorage()
#     admins = Rmember.objects.filter(role='admin')
#     for admin in admins:
#         if admin.email != 'meitronce1395@gmail.com' and admin.email != 'chikamasauesugi@gmail.com' and admin.email != 't-tarumi@crest.ocn.ne.jp'\
#         and admin.email != 'alertingjames@gmail.com' and admin.email != 'yamamoto_h@nac-om.com' and admin.email != 'rakubaru2020@gmail.com':
#             if admin.picture_url != '':
#                 fname = admin.picture_url.replace(settings.URL + '/media/', '')
#                 fs.delete(fname)
#             admin.delete()

#             routes = Route.objects.filter(member_id=admin.pk)
#             for route in routes:
#                 points = Rpoint.objects.filter(route_id=route.pk)
#                 for pnt in points:
#                     pnt.delete()
#                 pins = Rpin.objects.filter(route_id=route.pk)
#                 for pin in pins:
#                     pin.delete()
#                 route.delete()

#             devices = Device.objects.filter(member_id=admin.pk)
#             devices.delete()

#             emps = Rmember.objects.filter(admin_id=admin.pk)
#             for emp in emps:
#                 routes = Route.objects.filter(member_id=emp.pk)
#                 for route in routes:
#                     points = Rpoint.objects.filter(route_id=route.pk)
#                     for pnt in points:
#                         pnt.delete()
#                     pins = Rpin.objects.filter(route_id=route.pk)
#                     for pin in pins:
#                         pin.delete()
#                     route.delete()
#                 devices = Device.objects.filter(member_id=emp.pk)
#                 devices.delete()

#             paids = Paid.objects.filter(member_id=admin.pk)
#             paids.delete()

#             areas = Area.objects.filter(admin_id=admin.pk)
#             for area in areas:
#                 sublocs = Sublocality.objects.filter(area_id=area.pk)
#                 sublocs.delete()
#                 assigns = AreaAssign.objects.filter(area_id=area.pk)
#                 assigns.delete()
#                 area.delete()

#     return HttpResponse('Success!')






























