# Generated by Django 2.2.3 on 2019-07-26 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20190726_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='p_ind',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='p_neg',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='p_pos',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='sentiment',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
    ]
