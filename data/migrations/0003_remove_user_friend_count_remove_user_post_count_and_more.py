# Generated by Django 5.1.6 on 2025-05-12 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_remove_post_topic_post_topics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='friend_count',
        ),
        migrations.RemoveField(
            model_name='user',
            name='post_count',
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('like', 'Like')], max_length=20),
        ),
    ]
