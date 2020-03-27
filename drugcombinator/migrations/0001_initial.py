# Generated by Django 2.2.10 on 2020-03-25 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Drug',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='ajouté')),
                ('name', models.CharField(max_length=128, verbose_name='nom')),
                ('slug', models.SlugField(unique=True, verbose_name='identifiant')),
                ('description', models.TextField(blank=True, default='', verbose_name='description')),
                ('_aliases', models.TextField(blank=True, default='', help_text='Un alias par ligne. Insensible à la casse.', verbose_name='dénominations')),
            ],
            options={
                'verbose_name': 'substance',
            },
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sym_id', models.PositiveIntegerField(default=0)),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='ajouté')),
                ('risk', models.IntegerField(choices=[(0, 'Inconnu'), (1, 'Neutre'), (2, 'Vigilance'), (3, 'Risqué'), (4, 'Dangereux')], default=0, verbose_name='risques')),
                ('pharmaco', models.IntegerField(choices=[(0, 'Inconnue'), (1, 'Neutre'), (2, 'Atténuation'), (3, 'Potentialisation')], default=0, verbose_name='pharmacologie')),
                ('risk_description', models.TextField(blank=True, default='', verbose_name='description')),
                ('effect_description', models.TextField(blank=True, default='', verbose_name='description')),
                ('from_substance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_interaction+', to='drugcombinator.Drug', verbose_name='substance')),
                ('to_substance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_interaction+', to='drugcombinator.Drug', verbose_name='substance')),
            ],
            options={
                'verbose_name': 'intéraction',
                'unique_together': {('from_substance', 'to_substance')},
            },
        ),
        migrations.AddField(
            model_name='drug',
            name='interactants',
            field=models.ManyToManyField(through='drugcombinator.Interaction', to='drugcombinator.Drug', verbose_name='Intéractants'),
        ),
    ]
