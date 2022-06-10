# Generated by Django 4.0.4 on 2022-06-01 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_subscription_user_delete_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='status',
            field=models.IntegerField(choices=[(1, 'being processed'), (2, 'done'), (3, 'canceled')], default=1),
        ),
    ]
