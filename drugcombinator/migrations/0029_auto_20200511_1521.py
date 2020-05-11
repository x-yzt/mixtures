# Generated by Django 3.0.6 on 2020-05-11 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drugcombinator', '0028_auto_20200511_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='dernière modification'),
        ),
        migrations.AlterField(
            model_name='drug',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='dernière modification'),
        ),
        migrations.AlterField(
            model_name='interaction',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='dernière modification'),
        ),
        migrations.AlterField(
            model_name='note',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='dernière modification'),
        ),
    ]