# Generated by Django 3.0.3 on 2020-02-10 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalbeti', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='urls',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
