# Generated by Django 3.2.7 on 2021-10-13 21:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_alter_book_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ['name']},
        ),
    ]