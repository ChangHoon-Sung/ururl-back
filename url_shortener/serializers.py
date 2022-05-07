import hashlib, requests
from rest_framework import serializers

from django.conf import settings
from django.utils import baseconv
from .models import RandomURL

SALT = settings.SALT

class RandomURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = RandomURL
        fields = '__all__'
