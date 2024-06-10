# Generated by Django 5.0.6 on 2024-06-05 03:54

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0007_history_rename_faqmodel_faq_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='is_correct',
        ),
        migrations.AddField(
            model_name='history',
            name='username',
            field=models.CharField(default=django.utils.timezone.now, max_length=100),
            preserve_default=False,
        ),
    ]
