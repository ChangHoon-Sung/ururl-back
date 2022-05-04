from django.db import models

# Create your models here.
class RandomURL(models.Model):
    id = models.AutoField(primary_key=True)
    origin = models.URLField(max_length=2000)
    hash_val = models.CharField(max_length=64, unique=True, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.origin