# Generated by Django 5.0.6 on 2024-06-05 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0010_rename_langchainfilter_knowledgegraph_title_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='knowledgegraph',
            old_name='rule',
            new_name='purpose',
        ),
    ]
