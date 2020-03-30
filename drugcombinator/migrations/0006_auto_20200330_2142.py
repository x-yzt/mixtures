# Generated by Django 2.2.10 on 2020-03-30 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drugcombinator', '0005_auto_20200327_0205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interaction',
            old_name='from_substance',
            new_name='from_drug',
        ),
        migrations.RenameField(
            model_name='interaction',
            old_name='to_substance',
            new_name='to_drug',
        ),
        migrations.AlterField(
            model_name='drug',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='drugs', to='drugcombinator.Category', verbose_name='catégorie'),
        ),
        migrations.AlterUniqueTogether(
            name='interaction',
            unique_together={('from_drug', 'to_drug')},
        ),
    ]
