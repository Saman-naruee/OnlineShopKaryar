# Generated by Django 4.2.15 on 2024-09-26 22:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_collection_level_collection_lft_collection_rght_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'permissions': [('view_history', 'Can View History')]},
        ),
    ]