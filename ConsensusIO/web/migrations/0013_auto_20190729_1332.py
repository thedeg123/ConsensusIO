# Generated by Django 2.2.3 on 2019-07-29 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_price_change_pct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='p_ind',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='p_neg',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='p_pos',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=3, null=True),
        ),
    ]
