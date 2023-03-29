# Generated by Django 4.1.5 on 2023-03-16 17:58

from django.db import migrations, models
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ("sbusers", "0002_remove_sbuserprofile_created_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sbuserprofile",
            name="chatgpt_plus_password",
            field=fernet_fields.fields.EncryptedTextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="sbuserprofile",
            name="chatgpt_plus_username",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="sbuserprofile",
            name="first_name",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="sbuserprofile",
            name="last_name",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="sbuserprofile",
            name="openai_key",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
