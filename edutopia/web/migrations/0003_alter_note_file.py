# Generated by Django 4.2.13 on 2024-06-30 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='file',
            field=models.FileField(upload_to='web/Storage/'),
        ),
    ]
