# Generated by Django 3.1 on 2023-06-08 02:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_reviewrating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reviewrating',
            old_name='ratings',
            new_name='rating',
        ),
    ]