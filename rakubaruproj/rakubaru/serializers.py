from rest_framework import serializers
from .models import Rmember, Route, Rpoint, Rpin, Area, Sublocality, AreaAssign, CompanyInfo, CustomerInfo, ProductInfo, DistributionAreaInfo, DistributionAreaGroupInfo, DistributionAreaGroup, DistributorInfo, LeaderInfo
from .models import DistributorGroupInfo, SubcontractorInfo, IndustryInfo

class RmemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rmember
        fields = ('__all__')

class RpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rpoint
        fields = ('__all__')

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('__all__')

class RpinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rpin
        fields = ('__all__')

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('__all__')

class SublocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Sublocality
        fields = ('__all__')


class AreaAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaAssign
        fields = ('__all__')


class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = ('__all__')

class CustomerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerInfo
        fields = ('__all__')


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ('__all__')


class DistributionAreaInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionAreaInfo
        fields = ('__all__')


class DistributionAreaGroupInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionAreaGroupInfo
        fields = ('__all__')


class DistributionAreaGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributionAreaGroup
        fields = ('__all__')


class DistributorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributorInfo
        fields = ('__all__')


class LeaderInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderInfo
        fields = ('__all__')


class DistributorGroupInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistributorGroupInfo
        fields = ('__all__')



class SubcontractorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubcontractorInfo
        fields = ('__all__')



class IndustryInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryInfo
        fields = ('__all__')









































































