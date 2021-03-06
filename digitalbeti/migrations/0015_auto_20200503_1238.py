# Generated by Django 3.0.3 on 2020-05-03 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digitalbeti', '0014_auto_20200329_1323'),
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
        migrations.AddField(
            model_name='digitalbetiuser',
            name='prr',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='digitalbetiuser',
            name='uk',
            field=models.CharField(blank=True, max_length=24, null=True),
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
        migrations.CreateModel(
            name='VLECompetition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=1000, verbose_name='Facebook Profile Link')),
                ('current_likes', models.IntegerField()),
                ('month', models.IntegerField()),
                ('year', models.IntegerField()),
                ('status', models.IntegerField(choices=[(0, 'PENDING'), (1, 'APPROVED')], default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='digitalbeti.DigitalBetiUser')),
            ],
        ),
    ]
