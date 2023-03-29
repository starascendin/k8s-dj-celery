from django.db import migrations

def update_exec_type(apps, schema_editor):
    Prompt = apps.get_model('contents', 'Prompt')
    prompts_to_update = Prompt.objects.filter(exec_type='YT_FINAL_SUMMARIZE')
    
    for prompt in prompts_to_update:
        prompt.exec_type = 'DEFAULT_YT_FINAL_SUMMARIZE'
        prompt.save()

class Migration(migrations.Migration):

    dependencies = [
        ("contents", "0006_alter_prompt_exec_type"),
    ]

    operations = [
        migrations.RunPython(update_exec_type),
    ]