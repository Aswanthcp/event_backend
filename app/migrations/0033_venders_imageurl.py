# Generated by Django 4.2 on 2023-06-13 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_remove_eventcoordinator_date_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='venders',
            name='imageUrl',
            field=models.CharField(default='', max_length=300),
        ),
    ]
