# Generated by Django 4.0.10 on 2024-01-20 07:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_rename_rating_review_my_rating_review_average_rating_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='my_rating',
            new_name='rating',
        ),
    ]