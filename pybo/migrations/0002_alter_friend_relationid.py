# Generated by Django 4.0.3 on 2022-06-01 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='RelationID',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]