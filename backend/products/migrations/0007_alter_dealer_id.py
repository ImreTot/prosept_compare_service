# Generated by Django 5.0 on 2023-12-06 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_remove_product_dealer_prices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealer',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]