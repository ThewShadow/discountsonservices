# Generated by Django 4.0.4 on 2022-06-26 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_subscription_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
