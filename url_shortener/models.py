from django.db import models

# Create your models here.
class URL(models.Model):
    class Meta:
        abstract = True

    origin = models.URLField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.origin


class RandomURL(URL):
    id = models.AutoField(primary_key=True)
    hash_val = models.CharField(max_length=64, unique=True, default=None, null=True)


class CustomURL(URL):
    id = models.CharField(max_length=64, primary_key=True)
    owner = models.ForeignKey('account.User', on_delete=models.CASCADE)