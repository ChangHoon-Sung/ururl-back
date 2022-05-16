from django.contrib import admin

# Register your models here.
from .models import RandomURL, CustomURL

class CustomURLAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'origin', 'created_at')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return CustomURL.objects.all()
        try:
            return CustomURL.objects.filter(owner_id=request.user.id)
        except:
            return CustomURL.objects.none()

admin.site.register(RandomURL)
admin.site.register(CustomURL, CustomURLAdmin)