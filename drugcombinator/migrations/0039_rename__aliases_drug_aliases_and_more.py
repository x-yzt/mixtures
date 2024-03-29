# Generated by Django 4.1 on 2022-08-17 19:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drugcombinator', '0038_alter_historicaldrug_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='drug',
            old_name='_aliases',
            new_name='aliases',
        ),
        migrations.RenameField(
            model_name='drug',
            old_name='_aliases_en',
            new_name='aliases_en',
        ),
        migrations.RenameField(
            model_name='drug',
            old_name='_aliases_fr',
            new_name='aliases_fr',
        ),
        migrations.RenameField(
            model_name='historicaldrug',
            old_name='_aliases',
            new_name='aliases',
        ),
        migrations.RenameField(
            model_name='historicaldrug',
            old_name='_aliases_en',
            new_name='aliases_en',
        ),
        migrations.RenameField(
            model_name='historicaldrug',
            old_name='_aliases_fr',
            new_name='aliases_fr',
        ),
    ]
