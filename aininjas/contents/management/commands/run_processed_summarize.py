from django.core.management.base import BaseCommand, CommandError
from aininjas.contents.models import  ContentSource, ContentProcessed, UserPromptRunVersion
from aininjas.contents.services import ContentService, ContentPromptOrchestrator, PromptService
from aininjas.sbusers.models import SbPublicUser, SbUserProfile

# from aininjas.users.models import SbContentsUser

from scripts.libs.yt_transcript_client import YtClient
from libs.supabase_client import SupabaseClient
from config.settings.base import YT_API_KEY, SUPABASE_KEY, SUPABASE_URL, ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


class Command(BaseCommand):
    help = "Take a Content source, it's chunks, and run them through prompts"

    def handle(self, *args, **options):
        """
        Take a content source, get its chunks, then pass to prompt service
        """
        yt_client = YtClient(YT_API_KEY)
        sb_client = SupabaseClient(SUPABASE_URL, SUPABASE_KEY, 
                                endpoint_url=ENDPOINT_URL, 
                                s3_key=AWS_ACCESS_KEY_ID, 
                                s3_secret=AWS_SECRET_ACCESS_KEY
                                )
        sb_user: SbUserProfile = SbUserProfile.objects.get(id="ecf408de-3f7d-4693-95c3-5d94772072a5")
        print("#sb_user", sb_user)
        content_service = ContentService(yt_client, sb_client)
        prompt_service = PromptService(sb_user.openai_key)
        orchestrator = ContentPromptOrchestrator(prompt_service=prompt_service, content_service=content_service)

        content: ContentSource = ContentSource.objects.get(id="c88e920e-8a3a-41f1-8488-918ba6911022")
        processed = content.contentprocessed_set.first()
        # chunks = content_service.chunk_yt_processed(processed)

        pcs = orchestrator.run_user_processed_prompt_version(
            sb_user, 
            processed,
            UserPromptRunVersion.PromptRunTypeChoice.YT_CHUNK_SUMMARIZE
            )
        print("#Chunkings pcs", pcs)
        pcs = orchestrator.run_user_processed_prompt_version(
            sb_user, 
            processed,
            UserPromptRunVersion.PromptRunTypeChoice.YT_FINAL_SUMMARIZE
            )
        print("#Finalize pcs", pcs)
        # pc = orchestrator.finalize_summary_for_processed(processed)
        # print("#pc", pc)


