# Generated by Django 3.0.4 on 2020-04-30 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalbeti', '0013_auto_20200429_1812'),
    ]

    operations = [
        migrations.CreateModel(
            name='StateVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('JAMMU AND KASHMIR', 'JAMMU AND KASHMIR'), ('TELANGANA', 'TELANGANA'), ('TAMIL NADU', 'TAMIL NADU'), ('CHHATTISGARH', 'CHHATTISGARH'), ('BIHAR', 'BIHAR'), ('UTTAR PRADESH', 'UTTAR PRADESH'), ('KERALA', 'KERALA'), ('MAHARASHTRA', 'MAHARASHTRA'), ('RAJASTHAN', 'RAJASTHAN'), ('HARYANA', 'HARYANA')], max_length=100, verbose_name='State')),
                ('video_url', models.CharField(max_length=550)),
                ('thumbnail', models.ImageField(blank=True, upload_to='state_video/')),
            ],
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(choices=[('JAMMU AND KASHMIR', 'JAMMU AND KASHMIR'), ('TELANGANA', 'TELANGANA'), ('TAMIL NADU', 'TAMIL NADU'), ('CHHATTISGARH', 'CHHATTISGARH'), ('BIHAR', 'BIHAR'), ('UTTAR PRADESH', 'UTTAR PRADESH'), ('KERALA', 'KERALA'), ('MAHARASHTRA', 'MAHARASHTRA'), ('RAJASTHAN', 'RAJASTHAN'), ('HARYANA', 'HARYANA')], max_length=100, verbose_name='State'),
        ),
        migrations.AlterField(
            model_name='digitalbetiuser',
            name='state',
            field=models.CharField(choices=[('JAMMU AND KASHMIR', 'JAMMU AND KASHMIR'), ('TELANGANA', 'TELANGANA'), ('TAMIL NADU', 'TAMIL NADU'), ('CHHATTISGARH', 'CHHATTISGARH'), ('BIHAR', 'BIHAR'), ('UTTAR PRADESH', 'UTTAR PRADESH'), ('KERALA', 'KERALA'), ('MAHARASHTRA', 'MAHARASHTRA'), ('RAJASTHAN', 'RAJASTHAN'), ('HARYANA', 'HARYANA')], max_length=100, null=True),
        ),
    ]