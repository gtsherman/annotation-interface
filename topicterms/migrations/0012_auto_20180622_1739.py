# Generated by Django 2.0 on 2018-06-22 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topicterms', '0011_auto_20180611_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qualitycheck',
            name='term',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='topicterms.Term'),
        ),
    ]
