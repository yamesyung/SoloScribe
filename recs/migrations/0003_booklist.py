# Generated by Django 4.0.10 on 2024-03-07 20:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recs', '0002_genre_location_booklocation_bookgenre'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goodreads_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recs.book')),
                ('list_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recs.reclist')),
            ],
        ),
    ]