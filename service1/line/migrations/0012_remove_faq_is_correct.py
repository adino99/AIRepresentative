# Generated by Django 5.0.6 on 2024-06-05 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0011_rename_rule_knowledgegraph_purpose'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faq',
            name='is_correct',
        ),
    ]