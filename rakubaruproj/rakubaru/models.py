from django.db import models

class Rmember(models.Model):
    admin_id = models.CharField(max_length=11)
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
    cumulative_distance = models.CharField(max_length=50)
    customerID = models.CharField(max_length=1000)
    subscriptionID = models.CharField(max_length=1000)
    subperiodend = models.CharField(max_length=50)

class Rpoint(models.Model):
    route_id = models.CharField(max_length=11)
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)
    comment = models.CharField(max_length=1000)
    time = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    status = models.CharField(max_length=20)

class Rpin(models.Model):
    member_id = models.CharField(max_length=11)
    route_id = models.CharField(max_length=11)
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)
    comment = models.CharField(max_length=1000)
    time = models.CharField(max_length=50)
    status = models.CharField(max_length=20)

class Route(models.Model):
    member_id = models.CharField(max_length=11)
    assign_id = models.CharField(max_length=11)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    start_time = models.CharField(max_length=50)
    end_time = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    speed = models.CharField(max_length=50)
    distance = models.CharField(max_length=50)
    reported_time = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    status2 = models.CharField(max_length=50)
    admin_desc = models.CharField(max_length=1000)


class Paid(models.Model):
    member_id = models.CharField(max_length=11)
    plan = models.CharField(max_length=50)
    paid_amount = models.CharField(max_length=50)
    paid_time = models.CharField(max_length=50)
    coupon_id = models.CharField(max_length=11)
    discount = models.CharField(max_length=50)
    discount_amount = models.CharField(max_length=50)


class Device(models.Model):
    member_id = models.CharField(max_length=11)
    device = models.CharField(max_length=100)
    connected_time = models.CharField(max_length=100)
    status = models.CharField(max_length=20)


class Coupon(models.Model):
    code = models.CharField(max_length=100)
    discount = models.CharField(max_length=11)
    expire_time = models.CharField(max_length=50)
    status = models.CharField(max_length=20)


class Area(models.Model):
    admin_id = models.CharField(max_length=11)
    area_name = models.CharField(max_length=200)
    copies = models.CharField(max_length=11)
    unit_price = models.CharField(max_length=50)
    allowance = models.CharField(max_length=50)
    amount = models.CharField(max_length=50)
    distance = models.CharField(max_length=50)
    client_dist = models.CharField(max_length=50)
    locarr = models.CharField(max_length=1000000)
    posted_time = models.CharField(max_length=50)
    clients = models.CharField(max_length=11)
    status = models.CharField(max_length=50)


class Sublocality(models.Model):
    area_id = models.CharField(max_length=11)
    loc_name = models.CharField(max_length=200)
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    locarr = models.CharField(max_length=1000000)
    status = models.CharField(max_length=50)


class AreaAssign(models.Model):
    admin_id = models.CharField(max_length=11)
    area_id = models.CharField(max_length=11)
    member_id = models.CharField(max_length=11)
    title = models.CharField(max_length=200)
    client_dist = models.CharField(max_length=50)
    distribution = models.CharField(max_length=100)
    start_time = models.CharField(max_length=50)
    end_time = models.CharField(max_length=50)
    assigned_time = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    copies = models.CharField(max_length=11)
    unit_price = models.CharField(max_length=50)
    allowance = models.CharField(max_length=50)
    amount = models.CharField(max_length=50)
    distance = models.CharField(max_length=50)
    customer = models.CharField(max_length=200)


class Product(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    productID = models.CharField(max_length=1000)


class Price(models.Model):
    product_id = models.CharField(max_length=11)
    price = models.CharField(max_length=11)
    priceID = models.CharField(max_length=1000)







































































