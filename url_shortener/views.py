import hashlib

from django.shortcuts import redirect
from django.utils import baseconv
from django.conf import settings

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError

from .serializers import CustomURLSerializer, RandomURLSerializer
from .models import RandomURL, CustomURL


# generate random shorten url
class RandomURLGenerator(generics.CreateAPIView):
    queryset = RandomURL.objects.all()
    serializer_class = RandomURLSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        SALT = settings.SALT
        url_obj: RandomURL = RandomURL.objects.create(**serializer.validated_data)
        url_obj.hash_val = hashlib.sha256((SALT + str(url_obj.id)).encode("utf-8")).hexdigest()
        postfix = baseconv.base62.encode(int(url_obj.hash_val[:10], 16))
        url_obj.save()
        return postfix

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            postfix = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                f"{settings.BASE_URL}/{postfix}",
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except ValidationError as e:
            return Response(f"Validation Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise Exception(f"Unknown Error: {e}")


# generate custom url
class CustomURLGenerator(generics.CreateAPIView):
    queryset = CustomURL.objects.all()
    serializer_class = CustomURLSerializer
    permission_classes = (IsAuthenticated,)
    
    def create(self, request):
        data = {'origin': request.data['origin'], 'id':request.data['id']}
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                f"{settings.BASE_URL}/{serializer.data['id']}",
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except ValidationError as e:
            return Response(f"Validation Error: {e}", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise Exception(f"Unknown Error: {e}")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


def get_postfix_type(postfix: str):
    if len(postfix) == 7 and postfix.isalnum():
        return 'random'
    else:
        return 'custom'

def redirect_random_url(request, postfix: str):
    hash_prefix = hex(baseconv.base62.decode(postfix))[2:]
    try:
        url_obj: RandomURL = (
            RandomURL.objects.filter(hash_val__startswith=hash_prefix)
            .order_by("-created_at")
            .first()
        )
        if url_obj is None:
            raise RandomURL.DoesNotExist
        return redirect(url_obj.origin) 
    except RandomURL.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def redirect_url(request, postfix):
    postfix_type = get_postfix_type(postfix)
    if postfix_type == 'custom':
        try:
            url_obj: CustomURL = CustomURL.objects.get(id=postfix)
            return redirect(url_obj.origin)
        except CustomURL.DoesNotExist:
            return redirect_random_url(request, postfix)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif postfix_type == 'random':
        return redirect_random_url(request, postfix)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
        

@api_view(["GET"])
@permission_classes([AllowAny])
def redirect_home(request):
    return redirect(settings.HOME_URL)
