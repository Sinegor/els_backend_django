# Generated by Django 4.2.3 on 2023-08-02 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lawyeruserinterface',
            options={'verbose_name': 'Пользователь-юрист', 'verbose_name_plural': 'Пользователи-юристы'},
        ),
        migrations.AlterModelOptions(
            name='userskind',
            options={'verbose_name': 'Вид пользователя', 'verbose_name_plural': 'Разновидности пользователей'},
        ),
        migrations.AlterField(
            model_name='clientuserinterface',
            name='current_requests',
            field=models.CharField(blank=True, max_length=200, verbose_name='Текущие запросы на помощь'),
        ),
        migrations.AlterField(
            model_name='clientuserinterface',
            name='history_of_requests',
            field=models.CharField(blank=True, max_length=200, verbose_name='История запросов'),
        ),
        migrations.AlterField(
            model_name='lawyeruserinterface',
            name='current_applications',
            field=models.CharField(blank=True, default=None, max_length=200, verbose_name='Текущие заказы'),
        ),
        migrations.AlterField(
            model_name='lawyeruserinterface',
            name='history_of_applications',
            field=models.CharField(blank=True, default=None, max_length=200, verbose_name='История заказов'),
        ),
    ]