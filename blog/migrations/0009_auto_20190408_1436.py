# Generated by Django 2.0 on 2019-04-08 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_merge_20190407_2025'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blog',
            options={'ordering': ['-create_time']},
        ),
    ]
