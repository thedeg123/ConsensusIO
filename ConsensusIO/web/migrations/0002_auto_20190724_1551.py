# Generated by Django 2.2.3 on 2019-07-24 21:51

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.DateField(default=datetime.datetime(2019, 7, 24, 21, 51, 21, 81291, tzinfo=utc)),
        ),
    ]