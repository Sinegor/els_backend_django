# Generated by Django 4.2.3 on 2023-08-29 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legalApplication', '0004_rename_lawer_legalapp_lawyer'),
    ]

    operations = [
        migrations.AddField(
            model_name='legalapp',
            name='city',
            field=models.CharField(default='dssd', max_length=100, verbose_name='город, в котором необходима помощь'),
        ),
    ]
