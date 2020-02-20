# Generated by Django 3.0.3 on 2020-02-13 00:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalbeti', '0005_auto_20200212_0340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beneficiarydata',
            name='fathers_occupation',
        ),
        migrations.RemoveField(
            model_name='beneficiarydata',
            name='mothers_occupation',
        ),
        migrations.AddField(
            model_name='beneficiarydata',
            name='facebook_link',
            field=models.CharField(blank=True, max_length=264, null=True, verbose_name='Facebook Profile Link'),
        ),
        migrations.AddField(
            model_name='beneficiarydata',
            name='personal_monthly_income',
            field=models.IntegerField(choices=[(0, '0-10,000'), (1, '10,000-20,000'), (2, '20,000+')], default=0),
        ),
        migrations.AddField(
            model_name='beneficiarydata',
            name='tc_count',
            field=models.IntegerField(default=0, verbose_name='Number of Training Computers'),
        ),
    ]