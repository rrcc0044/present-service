# Generated by Django 2.1 on 2018-08-20 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_attendance_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='clock_out',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
