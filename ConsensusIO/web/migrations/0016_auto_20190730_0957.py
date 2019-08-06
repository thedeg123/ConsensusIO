# Generated by Django 2.2.3 on 2019-07-30 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0015_company_last_blank_day'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='last_blank_day',
        ),
        migrations.AddField(
            model_name='company',
            name='last_checked',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='sentiment',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=1, null=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
