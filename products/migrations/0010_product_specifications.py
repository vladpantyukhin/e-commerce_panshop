# Generated by Django 4.1.4 on 2023-01-18 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_alter_product_short_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='specifications',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
