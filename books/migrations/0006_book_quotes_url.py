# Generated by Django 4.0.10 on 2024-12-06 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_reviewtag_delete_booktag'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='quotes_url',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]