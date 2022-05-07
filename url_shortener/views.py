import hashlib, requests

from django.shortcuts import redirect
from django.utils import baseconv
from django.conf import settings
from django.http import HttpResponse

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError

from .serializers import RandomURLSerializer
from .models import RandomURL


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
        origin = request.data.get("origin")

        if not (origin.startswith("http://") or origin.startswith("https://")):
            try:
                res = requests.head("https://" + origin, allow_redirects=True, timeout=3)
                if res.status_code / 100 in (2, 3):
                    origin = "https://" + origin
            except:
                origin = "http://" + origin

        serializer = self.get_serializer(data={"origin": origin})
        try:
            serializer.is_valid(raise_exception=True)
            postfix = self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return HttpResponse(
                f"{settings.BASE_URL}/{postfix}",
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except ValidationError:
            return HttpResponse("Invalid URL", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise Exception(f"Unknown Error: {e}")


@api_view(["GET"])
@permission_classes([AllowAny])
def redirect_url(request, postfix):
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
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def redirect_home(request):
    return redirect(settings.HOME_URL)
