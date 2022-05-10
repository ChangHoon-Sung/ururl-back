from string import ascii_lowercase as lowercase, digits
import requests

from django.core.validators import URLValidator

from rest_framework import serializers

from .models import CustomURL, RandomURL


def attach_scheme(origin):
    try:
        res = requests.head("https://" + origin, allow_redirects=True, timeout=1)
        if res.status_code / 100 in (2, 3):
            origin = "https://" + origin
    except:
        origin = "http://" + origin
    return origin


class RandomURLSerializer(serializers.ModelSerializer):
    origin = serializers.CharField(max_length=2000)

    class Meta:
        model = RandomURL
        fields = "__all__"

    def validate_origin(self, value):
        if not (value.startswith("http://") or value.startswith("https://")):
            value = attach_scheme(value)

        return value


class CustomURLSerializer(serializers.ModelSerializer):
    origin = serializers.CharField(max_length=2000)

    class Meta:
        model = CustomURL
        fields = "id", "origin"

    def validate_id(self, value):
        if len(value) == 7 and (
            RandomURL.objects.all().filter(hash_val__startswith=value).exists()
            or CustomURL.objects.all().filter(id=value).exists()
        ):
            raise serializers.ValidationError("This id is already used.")

        if len(value) > 64:
            raise serializers.ValidationError("ID too long. Max length is 64.")

        for char in value:
            if char not in lowercase + digits + "-":
                raise serializers.ValidationError(
                    "Invalid ID. Lower-case alphabets, numbers, and hyphen(-) are allowed."
                )

        return value

    def validate_origin(self, value):
        if not (value.startswith("http://") or value.startswith("https://")):
            value = attach_scheme(value)
        
        URLValidator()(value)
        return value
