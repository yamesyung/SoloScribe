# Generated by Django 4.0.10 on 2024-11-04 15:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_review_author_lf_review_average_rating_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='rating_count',
            new_name='ratings_count',
        ),
        migrations.RenameField(
            model_name='book',
            old_name='rating_counts',
            new_name='ratings_count',
        ),
        migrations.RenameField(
            model_name='book',
            old_name='review_counts',
            new_name='reviews_count',
        ),
    ]
