# Generated by Django 2.2.13 on 2021-08-13 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '7442_delete_manifest_images_table'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='node',
            name='unique_nodename_nodegroup',
        ),
        migrations.AddField(
            model_name='maplayer',
            name='sortorder',
            field=models.IntegerField(null=True),
        ),
    ]
