# Generated by Django 5.0.6 on 2024-06-16 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='msg_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
