# Generated by Django 2.2.16 on 2022-04-12 18:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220119_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(limit_value=15, message='Длина этого поля должна быть не менее 15 символов')]),
        ),
    ]
