# Generated by Django 4.0.10 on 2024-02-12 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0012_bookgenre'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BookGenre',
            new_name='Genre',
        ),
    ]