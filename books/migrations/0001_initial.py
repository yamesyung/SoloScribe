# Generated by Django 4.0.10 on 2024-08-21 15:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('url', models.CharField(max_length=400)),
                ('author_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('birth_date', models.DateTimeField(blank=True, null=True)),
                ('death_date', models.DateTimeField(blank=True, null=True)),
                ('genres', models.TextField(blank=True, null=True)),
                ('influences', models.TextField(blank=True, null=True)),
                ('avg_rating', models.FloatField(blank=True, null=True)),
                ('reviews_count', models.IntegerField(blank=True, null=True)),
                ('rating_count', models.IntegerField(blank=True, null=True)),
                ('about', models.TextField(blank=True, null=True)),
                ('processed_ner', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AuthorLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('updated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('url', models.CharField(max_length=200)),
                ('goodreads_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('genres', models.TextField(blank=True, null=True)),
                ('author', models.TextField(max_length=300)),
                ('publish_date', models.DateTimeField(blank=True, null=True)),
                ('publisher', models.CharField(blank=True, max_length=200, null=True)),
                ('characters', models.TextField(blank=True, null=True)),
                ('rating_counts', models.IntegerField(blank=True, null=True)),
                ('review_counts', models.IntegerField(blank=True, null=True)),
                ('number_of_pages', models.IntegerField(blank=True, null=True)),
                ('places', models.TextField(blank=True, null=True)),
                ('image_url', models.CharField(blank=True, max_length=300, null=True)),
                ('cover_local_path', models.CharField(blank=True, max_length=300, null=True)),
                ('rating_histogram', models.CharField(blank=True, max_length=100, null=True)),
                ('language', models.CharField(blank=True, max_length=100, null=True)),
                ('series', models.CharField(blank=True, max_length=500, null=True)),
                ('scrape_status', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('latitude', models.CharField(blank=True, max_length=50, null=True)),
                ('longitude', models.CharField(blank=True, max_length=50, null=True)),
                ('updated', models.BooleanField(default=False)),
                ('requested', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=200)),
                ('additional_authors', models.TextField(blank=True, null=True)),
                ('isbn', models.CharField(blank=True, max_length=50, null=True)),
                ('isbn13', models.CharField(blank=True, max_length=50, null=True)),
                ('rating', models.IntegerField()),
                ('year_published', models.IntegerField(blank=True, null=True)),
                ('original_publication_year', models.IntegerField(blank=True, null=True)),
                ('date_read', models.DateField(blank=True, null=True)),
                ('date_added', models.DateField(blank=True, null=True)),
                ('bookshelves', models.CharField(max_length=200)),
                ('review_content', models.TextField(blank=True, null=True)),
                ('private_notes', models.TextField(blank=True, null=True)),
                ('read_count', models.IntegerField()),
                ('owned_copies', models.IntegerField()),
                ('goodreads_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book')),
            ],
            options={
                'ordering': ['-date_added'],
            },
        ),
        migrations.CreateModel(
            name='BookLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goodreads_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book')),
                ('location_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.location')),
            ],
        ),
        migrations.CreateModel(
            name='BookGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.genre')),
                ('goodreads_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book')),
            ],
        ),
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('awarded_at', models.IntegerField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=300, null=True)),
                ('goodreads_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book')),
            ],
        ),
        migrations.CreateModel(
            name='AuthorNER',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gpe', models.TextField(blank=True, null=True)),
                ('loc', models.TextField(blank=True, null=True)),
                ('person', models.TextField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.author')),
            ],
        ),
        migrations.CreateModel(
            name='AuthLoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.author')),
                ('authorlocation_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.authorlocation')),
            ],
        ),
    ]
