# Generated by Django 2.2.16 on 2022-03-03 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='created',
            new_name='pub_date',
        ),
    ]
