# Generated by Django 2.2.16 on 2022-04-18 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20220417_0854'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created']},
        ),
    ]
