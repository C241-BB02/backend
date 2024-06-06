# Generated by Django 4.2.13 on 2024-06-06 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bb_app', '0005_remove_photo_url_photo_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(default='This is the description field.'),
        ),
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.BigIntegerField(default='10000'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='user_id',
            field=models.IntegerField(),
        ),
    ]
