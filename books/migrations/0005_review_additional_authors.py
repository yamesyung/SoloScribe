# Generated by Django 4.0.10 on 2024-02-02 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_rename_last_updated_book_last_uploaded'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='additional_authors',
            field=models.TextField(blank=True, null=True),
        ),
    ]