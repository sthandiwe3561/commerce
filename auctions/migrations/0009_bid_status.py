# Generated by Django 5.1.4 on 2025-01-24 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_rename_price_product_starting_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
