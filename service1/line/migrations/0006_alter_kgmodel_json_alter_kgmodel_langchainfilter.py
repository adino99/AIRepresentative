# Generated by Django 5.0.6 on 2024-06-05 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('line', '0005_alter_kgmodel_json'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kgmodel',
            name='json',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='kgmodel',
            name='langchainfilter',
            field=models.CharField(max_length=100),
        ),
    ]