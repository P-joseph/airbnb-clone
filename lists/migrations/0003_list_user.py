# Generated by Django 2.2.5 on 2022-01-24 06:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lists', '0002_list_rooms'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.fields.CharField, related_name='list', to=settings.AUTH_USER_MODEL),
        ),
    ]