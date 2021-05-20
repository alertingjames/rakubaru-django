from django.db import models

class Rmember(models.Model):
    admin_id = models.CharField(max_length=11, default="0")
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=80)
    password = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=30)
    picture_url = models.CharField(max_length=1000)
    role = models.CharField(max_length=30)
    registered_time = models.CharField(max_length=50)
    device = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    plan = models.CharField(max_length=50)
    planned_members = models.CharField(max_length=50)
    pay_token = models.CharField(max_length=1000)
    cumulative_distance = models.CharField(max_length=50, default="0")
    customerID = models.CharField(max_length=1000)
    subscriptionID = models.CharField(max_length=1000)
    subperiodend = models.CharField(max_length=50)
    subscription_status = models.CharField(max_length=50)

class Rpoint(models.Model):
    route_id = models.CharField(max_length=11, default="0")
    lat = models.CharField(max_length=50, default="0")
    lng = models.CharField(max_length=50, default="0")
    comment = models.CharField(max_length=1000)
    time = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    status = models.CharField(max_length=20)

class Rpin(models.Model):
    member_id = models.CharField(max_length=11, default="0")
    route_id = models.CharField(max_length=11, default="0")
    lat = models.CharField(max_length=50, default="0")
    lng = models.CharField(max_length=50, default="0")
    comment = models.CharField(max_length=1000)
    time = models.CharField(max_length=50)
    status = models.CharField(max_length=20)

class Route(models.Model):
    member_id = models.CharField(max_length=11, default="0")
    assign_id = models.CharField(max_length=11, default="0")
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    start_time = models.CharField(max_length=50, default="0")
    end_time = models.CharField(max_length=50, default="0")
    duration = models.CharField(max_length=50, default="0")
    speed = models.CharField(max_length=50, default="0")
    distance = models.CharField(max_length=50, default="0")
    reported_time = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    status2 = models.CharField(max_length=50)
    admin_desc = models.CharField(max_length=1000)
    area_name = models.CharField(max_length=100)
    assign_title = models.CharField(max_length=200)


class Paid(models.Model):
    member_id = models.CharField(max_length=11, default="0")
    plan = models.CharField(max_length=50)
    paid_amount = models.CharField(max_length=50, default="0")
    paid_time = models.CharField(max_length=50)
    coupon_id = models.CharField(max_length=11, default="0")
    discount = models.CharField(max_length=50)
    discount_amount = models.CharField(max_length=50)
    plan_members = models.CharField(max_length=11)


class Device(models.Model):
    member_id = models.CharField(max_length=11)
    device = models.CharField(max_length=100)
    connected_time = models.CharField(max_length=100)
    status = models.CharField(max_length=20)


class Coupon(models.Model):
    code = models.CharField(max_length=100)
    discount = models.CharField(max_length=11, default="0")
    expire_time = models.CharField(max_length=50)
    status = models.CharField(max_length=20)


class Area(models.Model):
    admin_id = models.CharField(max_length=11, default="0")
    area_name = models.CharField(max_length=200)
    copies = models.CharField(max_length=11, default="0")
    unit_price = models.CharField(max_length=50, default="0")
    allowance = models.CharField(max_length=50, default="0")
    amount = models.CharField(max_length=50, default="0")
    distance = models.CharField(max_length=50, default="0")
    client_dist = models.CharField(max_length=50, default="0")
    locarr = models.CharField(max_length=1000000)
    posted_time = models.CharField(max_length=50)
    clients = models.CharField(max_length=11)
    status = models.CharField(max_length=50)
    prefecture = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)


class Sublocality(models.Model):
    area_id = models.CharField(max_length=11)
    loc_name = models.CharField(max_length=200)
    lat = models.CharField(max_length=50, default="0")
    lng = models.CharField(max_length=50, default="0")
    color = models.CharField(max_length=20)
    locarr = models.CharField(max_length=1000000)
    status = models.CharField(max_length=50)


class AreaAssign(models.Model):
    admin_id = models.CharField(max_length=11)
    area_id = models.CharField(max_length=11, default="0")
    member_id = models.CharField(max_length=11, default="0")
    title = models.CharField(max_length=200)
    client_dist = models.CharField(max_length=50)
    distribution = models.CharField(max_length=100)
    start_time = models.CharField(max_length=50, default="0")
    end_time = models.CharField(max_length=50, default="0")
    assigned_time = models.CharField(max_length=50, default="0")
    status = models.CharField(max_length=50)
    copies = models.CharField(max_length=11, default="0")
    unit_price = models.CharField(max_length=50, default="0")
    allowance = models.CharField(max_length=50, default="0")
    amount = models.CharField(max_length=50, default="0")
    distance = models.CharField(max_length=50)
    customer = models.CharField(max_length=200)


class Product(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    productID = models.CharField(max_length=1000)


class Price(models.Model):
    product_id = models.CharField(max_length=11)
    price = models.CharField(max_length=11, default="0")
    priceID = models.CharField(max_length=1000)



###########################################################################################################################

class ZPref1(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref01(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref2(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref3(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref4(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref5(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref6(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref7(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref8(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref9(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref10(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref11(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref12(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref13(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref14(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref15(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)



class ZPref16(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref17(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref18(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref19(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref20(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref21(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref22(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref23(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref24(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref25(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref26(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref27(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref28(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref29(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref30(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref31(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref32(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref33(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref34(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref35(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref36(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref37(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref38(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref39(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref40(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref41(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref42(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref43(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref44(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref45(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref46(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)


class ZPref47(models.Model):
    PREF_NAME = models.CharField(max_length=100)
    CITY_NAME = models.CharField(max_length=100)
    S_NAME = models.CharField(max_length=100)
    COORDS_JSON = models.CharField(max_length=10000000000)

















