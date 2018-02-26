# Generated by Django 2.0 on 2018-02-22 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topicterms', '0003_auto_20171222_2306'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTerm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topicterms.Document')),
            ],
        ),
        migrations.RemoveField(
            model_name='term',
            name='documents',
        ),
        migrations.AddField(
            model_name='documentterm',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topicterms.Term'),
        ),
    ]
