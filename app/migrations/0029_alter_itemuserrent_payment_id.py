# Generated by Django 4.2 on 2023-06-10 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_itemuserrent_date_bookedto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemuserrent',
            name='payment_id',
            field=models.CharField(default='111111111', max_length=300),
        ),
    ]
