from django.contrib import admin

# Register your models here.
from .models import RandomURL, CustomURL

admin.site.register(RandomURL)
admin.site.register(CustomURL)