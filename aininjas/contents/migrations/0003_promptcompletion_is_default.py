# Generated by Django 4.1.5 on 2023-03-20 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contents", "0002_remove_prompt_meta_json_blob"),
    ]

    operations = [
        migrations.AddField(
            model_name="promptcompletion",
            name="is_default",
            field=models.BooleanField(default=False),
        ),
    ]
