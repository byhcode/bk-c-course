# Generated by Django 3.2.4 on 2022-04-26 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_manager", "0006_alter_user_account"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usertag",
            name="tag_value",
            field=models.CharField(max_length=20, unique=True, verbose_name="标签值"),
        ),
    ]
