# Generated by Django 5.0.13 on 2025-08-01 18:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('advisors', '0001_initial'),
        ('students', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinalProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('submission_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('in_progress', 'ກຳລັງດຳເນີນການ'), ('completed', 'ສຳເລັດ'), ('pending_review', 'ລໍຖ້າກວດສອບ')], default='in_progress', max_length=20)),
                ('advisor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leading_projects', to='advisors.advisor')),
                ('committee_members', models.ManyToManyField(blank=True, related_name='committee_projects', to='advisors.advisor')),
                ('students', models.ManyToManyField(related_name='projects', to='students.student')),
            ],
        ),
    ]
