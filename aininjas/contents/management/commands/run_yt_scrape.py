from django.core.management.base import BaseCommand, CommandError
from aininjas.contents.models import  ContentSource, ContentProcessed, UserPromptRunVersion
from aininjas.contents.services import ContentService, ContentPromptOrchestrator, PromptService
from aininjas.sbusers.models import SbPublicUser, SbUserProfile

from scripts.libs.yt_transcript_client import YtClient
from libs.supabase_client import SupabaseClient
from config.settings.base import YT_API_KEY, SUPABASE_KEY, SUPABASE_URL, ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

class Command(BaseCommand):
    help = 'Scrape a YT vid and store transcripts'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        url = 'https://www.youtube.com/watch?v=fKca5JPPHpU'
        
        
        yt_client = YtClient(YT_API_KEY)
        sb_client = SupabaseClient(SUPABASE_URL, SUPABASE_KEY, 
                                endpoint_url=ENDPOINT_URL, 
                                s3_key=AWS_ACCESS_KEY_ID, 
                                s3_secret=AWS_SECRET_ACCESS_KEY
                                )
        
        content_service = ContentService(yt_client, sb_client)
        sb_user: SbUserProfile = SbUserProfile.objects.get(id="ecf408de-3f7d-4693-95c3-5d94772072a5")
        prompt_service = PromptService(sb_user.openai_key)
        orchestrator = ContentPromptOrchestrator(prompt_service=prompt_service, content_service=content_service)

        results = content_service.run_yt_url_to_chunks(
            url,podcast_type='MONO'
            )
        print('# results', results)
