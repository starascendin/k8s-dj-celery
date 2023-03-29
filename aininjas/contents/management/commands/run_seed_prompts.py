from django.core.management.base import BaseCommand, CommandError
from aininjas.contents.models import ContentSource, ContentProcessed, Prompt
from aininjas.contents.services import ContentService, ContentPromptOrchestrator, PromptService

from config.settings.base import YT_API_KEY
from scripts.libs.yt_transcript_client import YtClient

import textwrap

class Command(BaseCommand):
    help = "Seed hardcoded prompts"

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        """
        Take a content source, get its chunks, then pass to prompt service
        """

        prompts = [Prompt(
            name="Default YT Chapter Summarization 1",
            prompt=textwrap.dedent("""                                   
            Prompt: 
            1. Summarize the unique ideas into bullet points.  Prefix the bullet points with annotation with timestamp in total seconds (seconds)
            2. Summarize the key lessons into bullet points.  Prefix the bullet points with annotation with timestamp in total seconds (seconds)
            """).strip(),
            exec_type="DEFAULT_CHUNK_SUMMARIZE"
        ), Prompt(
            name="Default Final Summarization 1",
            prompt=textwrap.dedent("""                                
            Prompt:
            1. Write 1 paragraph summarizing everything.
            2. Group bullet points into categories and annotate with timestamp in total seconds (seconds).



            """).strip(),
            exec_type="DEFAULT_YT_FINAL_SUMMARIZE"
        )]
        for p in prompts:
            try:
                result = Prompt.objects.get_or_create(
                    name=p.name,
                    defaults={
                        'prompt': p.prompt,
                        'exec_type': p.exec_type
                    }
                )
                print("# seeding prompts: ", result)
                # p.save()
            except Exception as e:
                print(e)
        