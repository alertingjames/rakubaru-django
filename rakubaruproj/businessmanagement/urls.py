from django.conf.urls import url
from . import views, tests

app_name='businessmanagement'

urlpatterns=[
    url(r'^$', views.index, name='index'),
    url(r'login', views.login, name='login'),
    url(r'response', views.response, name='response'),
    url(r'logout', views.logout, name='logout'),
    ########### Company Master ##############################################################################
    url(r'company-master', views.company_master, name='company_master'),
    url(r'companyinforegister', views.company_register, name='companyinforegister'),
    url(r'delcompanyinfo', views.delete_company_info, name='delcompanyinfo'),
    ########### Customer Master ##############################################################################
    url(r'customer-master', views.customer_master, name='customer_master'),
    url(r'customerinforegister', views.customer_register, name='customerinforegister'),
    url(r'delcustomerinfo', views.delete_customer_info, name='delcustomerinfo'),
    ########### Product Master ##############################################################################
    url(r'product-master', views.product_master, name='product_master'),
    url(r'productinforegister', views.product_register, name='productinforegister'),
    url(r'delproductinfo', views.delete_product_info, name='delproductinfo'),
    ########### Distribution Area Master ##############################################################################
    url(r'distribution-area-master', views.distribution_area_master, name='distribution-area-master'),
    url(r'distributionareainforegister', views.distribution_area_register, name='distributionareainforegister'),
    url(r'deldistributionareainfo', views.delete_distribution_area_info, name='deldistributionareainfo'),
    ########### Distribution Area Group Master ##############################################################################
    url(r'distribution-area-group-master', views.distribution_area_group_master, name='distribution-area-group-master'),
    url(r'dareagroupinforegister', views.distribution_area_group_register, name='dareagroupinforegister'),
    url(r'deldareagroupinfo', views.delete_distribution_area_group_info, name='deldareagroupinfo'),
    ########### Distributor Master ##############################################################################
    url(r'distributor-master', views.distributor_master, name='distributor-master'),
    url(r'distributorinforegister', views.distributor_register, name='distributorinforegister'),
    url(r'deldistributorinfo', views.delete_distributor_info, name='deldistributorinfo'),
    ########### Leader Master ##############################################################################
    url(r'leader-master', views.leader_master, name='leader-master'),
    url(r'leaderinforegister', views.leader_register, name='leaderinforegister'),
    url(r'delleaderinfo', views.delete_leader_info, name='delleaderinfo'),
    ########### Distributor Group Master ##############################################################################
    url(r'distributor-group-master', views.distributor_group_master, name='distributor-group-master'),
    url(r'distributorgroupinforegister', views.distributor_group_register, name='distributorgroupinforegister'),
    url(r'deldistributorgroupinfo', views.delete_distributor_group_info, name='deldistributorgroupinfo'),
    ########### Subcontractor Master ##############################################################################
    url(r'subcontractor-master', views.subcontractor_master, name='subcontractor-master'),
    url(r'subcontractorinforegister', views.subcontractor_register, name='subcontractorinforegister'),
    url(r'delsubcontractorinfo', views.delete_subcontractor_info, name='delsubcontractorinfo'),
    ########### Industry Master ##############################################################################
    url(r'other-industry-master', views.industry_master, name='other-industry-master'),
    url(r'industryinforegister', views.industry_register, name='industryinforegister'),
    url(r'delindustryinfo', views.delete_industry_info, name='delindustryinfo'),
    ########### Distribution Type Master ##############################################################################
    url(r'other-distribution-type-master', views.distribution_type_master, name='other-distribution-type-master'),
    url(r'distributiontypeinfosave', views.distribution_type_save, name='distributiontypeinfosave'),


]


















































































