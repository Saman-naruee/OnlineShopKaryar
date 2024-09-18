# Generated by Django 4.2.15 on 2024-09-18 16:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_rename_descriptions_review_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='id',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='id',
        ),
        migrations.AddField(
            model_name='cart',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]