# Generated by Django 5.1 on 2024-08-29 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_remove_product_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(default=' '),
        ),
    ]