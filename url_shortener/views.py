import hashlib, requests
from django.forms import ValidationError

from django.shortcuts import redirect
from django.utils import baseconv
from django.conf import settings
from django.core.validators import URLValidator
from django.http import HttpResponse

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework import status

from .models import RandomURL


SALT = settings.SALT

BASE_URL = 'https://ururl.life'
HOME_URL = 'https://enjoy.ururl.life'


# generate random shorten url
@api_view(["POST"])
@permission_classes([AllowAny])
def generate_random_url(request):
    url_obj = None
    origin = request.data['origin']

    if not (origin.startswith('http://') or origin.startswith('https://')):
        try:
            res = requests.head('https://' + origin, allow_redirects=True, timeout=3)
            if res.status_code / 100 in (2, 3):
                origin = 'https://' + origin
        except:
            origin = 'http://' + origin
    
    try:
        URLValidator()(origin)
    except ValidationError as e:
        return HttpResponse('URL pattern doesn\'t match', status=status.HTTP_400_BAD_REQUEST)

    url_obj: RandomURL = RandomURL.objects.create(origin=origin)

    url_obj.hash_val = hashlib.sha256((SALT+str(url_obj.id)).encode('utf-8')).hexdigest()
    postfix = baseconv.base62.encode(int(url_obj.hash_val[:10], 16))
    url_obj.save()
    return HttpResponse(f'{BASE_URL}/{postfix}', status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def redirect_url(request, postfix):
    hash_prefix = hex(baseconv.base62.decode(postfix))[2:]

    try:
        url_obj: RandomURL = RandomURL.objects.filter(hash_val__startswith=hash_prefix).order_by('-created_at').first()
        if url_obj is None:
            raise RandomURL.DoesNotExist
        return redirect(url_obj.origin)
    except RandomURL.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def redirect_home(request):
    return redirect(HOME_URL)