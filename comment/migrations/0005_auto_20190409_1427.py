# Generated by Django 2.0 on 2019-04-09 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0004_auto_20190408_2315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='comment_context',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='comment_user',
            new_name='user',
        ),
    ]