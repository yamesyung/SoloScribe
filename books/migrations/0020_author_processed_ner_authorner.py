# Generated by Django 4.0.10 on 2024-02-22 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0019_alter_location_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='processed_ner',
            field=models.BooleanField(default=False),
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
    ]