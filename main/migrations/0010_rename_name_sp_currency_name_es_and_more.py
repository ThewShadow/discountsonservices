# Generated by Django 4.0.4 on 2022-06-27 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_currency_name_fr_currency_name_il_currency_name_sp_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='currency',
            old_name='name_sp',
            new_name='name_es',
        ),
        migrations.RenameField(
            model_name='offer',
            old_name='name_sp',
            new_name='name_es',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='name_sp',
            new_name='name_es',
        ),
        migrations.RenameField(
            model_name='rate',
            old_name='name_sp',
            new_name='name_es',
        ),
    ]