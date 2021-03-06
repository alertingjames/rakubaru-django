# Generated by Django 3.1.2 on 2020-10-26 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rmember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_id', models.CharField(max_length=11)),
                ('name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=80)),
                ('password', models.CharField(max_length=30)),
                ('phone_number', models.CharField(max_length=30)),
                ('picture_url', models.CharField(max_length=1000)),
                ('role', models.CharField(max_length=30)),
                ('registered_time', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_id', models.CharField(max_length=11)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=1000)),
                ('start_time', models.CharField(max_length=50)),
                ('end_time', models.CharField(max_length=50)),
                ('duration', models.CharField(max_length=50)),
                ('speed', models.CharField(max_length=50)),
                ('distance', models.CharField(max_length=50)),
                ('reported_time', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Rpin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.CharField(max_length=11)),
                ('lat', models.CharField(max_length=50)),
                ('lng', models.CharField(max_length=50)),
                ('comment', models.CharField(max_length=1000)),
                ('time', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Rpoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.CharField(max_length=11)),
                ('lat', models.CharField(max_length=50)),
                ('lng', models.CharField(max_length=50)),
                ('comment', models.CharField(max_length=1000)),
                ('time', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=20)),
            ],
        ),
    ]
