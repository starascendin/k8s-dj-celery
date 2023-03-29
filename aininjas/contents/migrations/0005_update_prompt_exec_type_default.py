from django.db import migrations

def update_exec_type(apps, schema_editor):
    Prompt = apps.get_model('contents', 'Prompt')
    prompts_to_update = Prompt.objects.filter(exec_type='DEFAULT')
    
    for prompt in prompts_to_update:
        prompt.exec_type = 'DEFAULT_CHUNK_SUMMARIZE'
        prompt.save()

class Migration(migrations.Migration):

    dependencies = [
        ("contents", "0004_alter_prompt_exec_type"),
    ]

    operations = [
        migrations.RunPython(update_exec_type),
    ]