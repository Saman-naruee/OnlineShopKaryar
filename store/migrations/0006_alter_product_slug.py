# Generated by Django 5.1 on 2024-08-29 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_product_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(auto_created=True, default=models.CharField(max_length=255)),
        ),
    ]
