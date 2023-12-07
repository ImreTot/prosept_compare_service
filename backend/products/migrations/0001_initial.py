# Generated by Django 4.2.7 on 2023-12-03 10:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dealer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='DealerPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_key', models.IntegerField(null=True)),
                ('price', models.FloatField(null=True)),
                ('product_url', models.URLField(unique=True)),
                ('product_name', models.CharField(max_length=250)),
                ('date', models.DateField()),
                ('marking_date', models.DateTimeField(null=True)),
                ('dealer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dealer_prices', to='products.dealer')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.CharField(max_length=100)),
                ('ean_13', models.FloatField(null=True)),
                ('name', models.CharField(max_length=250)),
                ('cost', models.FloatField(null=True)),
                ('recommended_price', models.FloatField(null=True)),
                ('category_id', models.IntegerField(null=True)),
                ('ozon_name', models.CharField(max_length=250)),
                ('name_1c', models.CharField(max_length=250)),
                ('wb_name', models.CharField(max_length=250)),
                ('ozon_article', models.CharField(max_length=250)),
                ('wb_article', models.CharField(max_length=250)),
                ('ym_article', models.CharField(max_length=250)),
                ('wb_article_td', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('total_markup_count', models.IntegerField()),
                ('none_chosen_count', models.IntegerField()),
                ('choices_order', models.JSONField()),
                ('chosen_options_stats', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='ProductDealerKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compliance_percentage', models.PositiveSmallIntegerField()),
                ('marking_date', models.DateTimeField(null=True)),
                ('choices_order', models.IntegerField(null=True)),
                ('dealer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.dealer')),
                ('key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matching_product', to='products.dealerprice')),
                ('product_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_dealer_keys', to='products.product')),
            ],
        ),
    ]
