# Generated by Django 3.0.8 on 2020-07-11 20:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auto_20200712_0137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='winner',
        ),
    ]
