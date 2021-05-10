from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from rakubaru import views
from rakubaru.views import run_task

urlpatterns = [

    # url(r'^admin/', admin.site.urls),
    url(r'^rakubaru/', include('rakubaru.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^superadmin', views.superadmin, name='superadmin'),
    url(r'^superlogin', views.superlogin, name='superlogin'),
    url(r'^employees', views.employees, name='employees'),
    url(r'^emreports', views.emreports, name='emreports'),
    url(r'^adminreports', views.adminreports, name='adminreports'),
    url(r'^allreports', views.allreports, name='allreports'),
    url(r'^empinmap', views.empinmap, name='empinmap'),
    url(r'^emroutemap', views.emroutemap, name='emroutemap'),
    url(r'^superlogout', views.superlogout, name='superlogout'),
    url(r'^allpayments', views.allpayments, name='allpayments'),
    url(r'^landing', views.openlanding, name='openlanding'),
    url(r'^couponpage',views.couponpage,  name='couponpage'),
    url(r'^createCoupon',views.createCoupon,  name='createCoupon'),
    url(r'^delcoupon',views.delcoupon,  name='delcoupon'),
    url(r'^monthcouponhistorydata',views.monthcouponhistorydata,  name='monthcouponhistorydata'),

    url(r'^test', views.test, name='test'),
    # url(r'^deltestadmins', views.deltestadmins, name='deltestadmins'),
]

run_task(repeat=43200,repeat_until=None)

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns=format_suffix_patterns(urlpatterns)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
