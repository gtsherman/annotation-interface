# Generated by Django 2.0 on 2018-02-22 23:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topicterms', '0004_auto_20180222_2050'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='complete',
            field=models.BooleanField(default=False),
        ),
    ]