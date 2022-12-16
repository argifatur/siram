# Generated by Django 4.1.3 on 2022-12-16 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0014_resep_author_resep_is_from_api_resep_kategori_resep_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmarks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_resep', models.CharField(max_length=255, null=True)),
                ('title_resep', models.CharField(max_length=255, null=True)),
                ('thumb_resep', models.CharField(max_length=255, null=True)),
                ('times_resep', models.CharField(max_length=255, null=True)),
                ('serving_resep', models.CharField(max_length=255, null=True)),
                ('difficulty_resep', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
