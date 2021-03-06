# Generated by Django 3.0.8 on 2020-07-11 20:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auto_20200712_0144'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='winner',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='wins', to=settings.AUTH_USER_MODEL),
        ),
    ]
