# Generated by Django 2.2.4 on 2019-08-24 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0018_auto_20190730_1910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='review',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]