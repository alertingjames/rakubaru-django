from rest_framework import serializers
from .models import Rmember, Route, Rpoint, Rpin, Area, Sublocality, AreaAssign

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










































