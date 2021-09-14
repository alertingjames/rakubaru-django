from django.conf.urls import url
from . import views, payment, export, tests

app_name='rakubaru'

urlpatterns=[

    ######################## Admin ###########################################################################################################

    url(r'^$', views.index, name='index'),
    url(r'ralogin', views.ralogin, name='ralogin'),
    url(r'rasublogin', views.rasublogin, name='rasublogin'),
    url(r'torasignup', views.rasignuppage, name='rasignuppage'),
    url(r'rasignup', views.rasignup, name='rasignup'),
    url(r'toraforgotpassword', views.raforgotpasswordpage, name='raforgotpasswordpage'),
    url(r'raforgotpassword', views.raforgotpassword, name='raforgotpassword'),
    url(r'raresetpassword', views.raresetpassword, name='raresetpassword'),
    url(r'rahome', views.rahome, name='rahome'),
    url(r'ralogout', views.ralogout, name='ralogout'),
    url(r'ranewemployee', views.ranewemployee, name='ranewemployee'),
    url(r'radelmember', views.radelmember, name='radelmember'),
    url(r'rapasswordchange', views.rapasswordchange, name='rapasswordchange'),
    url(r'rachangepassword', views.rachangepassword, name='rachangepassword'),
    url(r'raallreports', views.raallreports, name='raallreports'),
    url(r'radelroute', views.radelroute, name='radelroute'),
    url(r'rauserreports', views.rauserreports, name='rauserreports'),
    url(r'rasearchreportbydate', views.rasearchreportbydate, name='rasearchreportbydate'),
    url(r'raopenroutemap', views.raopenroutemap, name='raopenroutemap'),
    url(r'getlastpoint', views.getlastpoint, name='getlastpoint'),
    url(r'rapinmap', views.rapinmap, name='rapinmap'),
    url(r'raeditroute', views.raeditroute, name='raeditroute'),
    url(r'raemployeeprocess', views.raemployeeprocess, name='raemployeeprocess'),

    ########################################################################################################################################################
    # url(r'ratoplan', views.ratoplan, name='ratoplan'),

    url(r'ratoplan', payment.toplan, name='toplan'),
    url(r'createproduct', payment.createproduct, name='createproduct'),
    url(r'racreatesubscription', payment.racreatesubscription, name='racreatesubscription'),
    url(r'rachangesubscription', payment.rachangesubscription, name='rachangesubscription'),
    url(r'rasubscriptiondelete', payment.rasubscriptiondelete, name='rasubscriptiondelete'),


    url(r'ratopay', views.ratopay, name='ratopay'),
    url(r'rapay', views.rapay, name='rapay'),
    url(r'rachecksubscription', views.rachecksubscription, name='rachecksubscription'),
    url(r'checkcoupon', views.checkcoupon, name='checkcoupon'),

    url(r'toareas', views.toareas, name='toareas'),
    url(r'areasetup', views.areasetup, name='areasetup'),
    url(r'postarea', views.postarea, name='postarea'),
    url(r'delarea', views.delarea, name='delarea'),
    url(r'editarea', views.editarea, name='editarea'),
    url(r'assignarea', views.assignarea, name='assignarea'),
    url(r'getallassigns', views.getallassigns, name='getallassigns'),
    url(r'tomember', views.tomember, name='tomember'),
    url(r'updatearea', views.updatearea, name='updatearea'),
    url(r'editassign', views.editassign, name='editassign'),
    url(r'delassign', views.delassign, name='delassign'),
    url(r'searcharea', views.searcharea, name='searcharea'),
    url(r'searchassign', views.searchassign, name='searchassign'),
    url(r'schassignbydate', views.schassignbydate, name='schassignbydate'),
    url(r'broadcast', views.broadcast, name='broadcast'),
    url(r'assignedworks', views.assignedworks, name='assignedworks'),

    url(r'radowngradesubscription', views.radowngradesubscription, name='radowngradesubscription'),
    url(r'raupgradesubscription', views.raupgradesubscription, name='raupgradesubscription'),
    # url(r'rasubscriptiondelete', views.rasubscriptiondelete, name='rasubscriptiondelete'),

    url(r'getmysubscriptions', views.getmysubscriptions, name='getmysubscriptions'),
    url(r'raallworksinarea', views.allassignedworks, name='allassignedworks'),
    url(r'kkkkk', export.exportassignedworksjson, name='exportassignedworksjson'),


    ######################### User #################################################################################################################

    url(r'login', views.login, name='login'),
    # url(r'signup', views.signup, name='signup'),
    url(r'forgotpassword', views.forgotpassword, name='forgotpassword'),
    url(r'resetpassword', views.resetpassword, name='resetpassword'),
    url(r'rstpwd', views.rstpwd, name='rstpwd'),
    url(r'updatemember', views.updatemember, name='updatemember'),
    url(r'passwordupdate', views.passwordupdate, name='passwordupdate'),
    url(r'uploadroute', views.uploadroute, name='uploadroute'),
    url(r'getmyroutes', views.getmyroutes, name='getmyroutes'),
    url(r'routedetails', views.routedetails, name='routedetails'),
    url(r'reportroute', views.reportroute, name='reportroute'),
    url(r'delroute', views.delroute, name='delroute'),
    url(r'savepin', views.savepin, name='savepin'),
    url(r'getmypins', views.getmypins, name='getmypins'),
    url(r'delpin', views.delpin, name='delpin'),
    url(r'logout', views.logout, name='logout'),
    url(r'editmember', views.editmember, name='editmember'),

    url(r'checkdevice', views.checkdevice, name='checkdevice'),
    url(r'checkrouteloading', views.checkrouteloading, name='checkrouteloading'),

    url(r'getAssignedAreas', views.getAssignedAreas, name='getAssignedAreas'),
    url(r'removeAssign', views.removeAssign, name='removeAssign'),
    url(r'getAreaSublocs', views.getAreaSublocs, name='getAreaSublocs'),

    url(r'submitDistance', views.submitDistance, name='submitDistance'),

    url(r'upRoute', views.upRoute, name='upRoute'),
    url(r'getMyCumulativeDistance', views.getMyCumulativeDistance, name='getMyCumulativeDistance'),

    url(r'upRTRoute', views.upRTRoute, name='upRTRoute'),
    url(r'routearea', views.routearea, name='routearea'),

    url(r'rmroute', views.rmroute, name='rmroute'),


    ########################################################### Server Maintenance #############################################################################

    url(r'startorendreporting', tests.startorendreporting, name='startorendreporting'),
    url(r'updatereportdatainrealtime', tests.updatereportdatainrealtime, name='updatereportdatainrealtime'),
    url(r'jsonfiletest', tests.jsonfiletest, name='jsonfiletest'),


    ############################################################ Export Files ######################################################################

    url(r'userscsvexport', export.userscsvexport, name='userscsvexport'),
    url(r'reportscsvexport', export.reportscsvexport, name='reportscsvexport'),
    url(r'assignscsvexport', export.assignscsvexport, name='assignscsvexport'),
    url(r'csvexport', export.csvexport, name='csvexport'),
    url(r'jsonexport', export.jsonexport, name='jsonexport'),
    url(r'qqqqq', export.assignreportscsvexport, name='assignreportscsvexport'),
    url(r'backup', export.data_backup, name='data_backup'),




    ########################################################## Test ############################################################################################

    url(r'ttttt', tests.points_count, name='tests_points_count'),
    url(r'kkkkk', tests.save_route, name='tests_save_route'),

]



















































