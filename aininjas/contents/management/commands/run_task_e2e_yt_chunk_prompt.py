from django.core.management.base import BaseCommand, CommandError
from aininjas.contents.models import  ContentSource, ContentProcessed, UserPromptRunVersion
from aininjas.contents.services import ContentService, ContentPromptOrchestrator, PromptService
from aininjas.sbusers.models import SbPublicUser, SbUserProfile

from scripts.libs.yt_transcript_client import YtClient
from libs.supabase_client import SupabaseClient
from config.settings.base import YT_API_KEY, SUPABASE_KEY, SUPABASE_URL, ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from aininjas.contents.tasks import task_transcribe_yt_content_to_prompt_completion


class Command(BaseCommand):
    help = 'Scrape a YT vid and store transcripts'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        url = 'https://www.youtube.com/watch?v=nYqeHIRKboM'
        
        
        user_profile: SbUserProfile = SbUserProfile.objects.get(id="19a1e545-58df-4d2f-a0be-7e30748c1eee")
        
        task_id = task_transcribe_yt_content_to_prompt_completion.delay(
            yt_url=url,
            podcast_type="MONO",
            user_id=user_profile.id,
        )
        print("# task_id", task_id)
        
