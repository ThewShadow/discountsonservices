# Generated by Django 4.0.4 on 2022-06-27 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_subscription_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='name_fr',
            field=models.CharField(default='', max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='currency',
            name='name_il',
            field=models.CharField(default='', max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='currency',
            name='name_sp',
            field=models.CharField(default='', max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='name_fr',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='name_il',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='offer',
            name='name_sp',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='name_fr',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='name_il',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='name_sp',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='rate',
            name='name_fr',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='rate',
            name='name_il',
            field=models.CharField(default='', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='rate',
            name='name_sp',
            field=models.CharField(default='', max_length=200, null=True),
        ),
    ]
