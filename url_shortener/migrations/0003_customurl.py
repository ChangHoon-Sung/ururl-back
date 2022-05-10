# Generated by Django 4.0.4 on 2022-05-10 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url_shortener', '0002_alter_randomurl_hash_val_alter_randomurl_origin'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomURL',
            fields=[
                ('origin', models.URLField(max_length=2000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
