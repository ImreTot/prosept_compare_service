# Generated by Django 4.2.4 on 2023-12-01 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productdealerkey_marking_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='productdealerkey',
            name='choices_order',
            field=models.IntegerField(null=True),
        ),
    ]