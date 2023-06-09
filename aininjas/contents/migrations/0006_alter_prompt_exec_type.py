# Generated by Django 4.1.5 on 2023-03-20 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contents", "0005_update_prompt_exec_type_default"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prompt",
            name="exec_type",
            field=models.CharField(
                choices=[
                    ("NONE", "NONE"),
                    ("DEFAULT_CHUNK_SUMMARIZE", "DEFAULT_CHUNK_SUMMARIZE"),
                    ("DEFAULT_YT_FINAL_SUMMARIZE", "DEFAULT_YT_FINAL_SUMMARIZE"),
                ],
                default="NONE",
                max_length=50,
            ),
        ),
    ]
