# Generated by Django 2.0 on 2019-04-09 15:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0005_auto_20190409_1427'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='text',
            new_name='comment_context',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='user',
            new_name='comment_user',
        ),
    ]