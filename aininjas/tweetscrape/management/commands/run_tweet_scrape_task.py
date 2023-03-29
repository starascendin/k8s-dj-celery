from django.core.management.base import BaseCommand, CommandError
from aininjas.contents.models import ContentSource, ContentProcessed
from aininjas.contents.services import ContentService, ContentPromptOrchestrator, PromptService

from config.settings.base import YT_API_KEY, SUPABASE_KEY, SUPABASE_URL
from scripts.libs.yt_transcript_client import YtClient
from libs.supabase_client import SupabaseClient
# from aininjas.contents.tasks import task_dl_transcripts_and_format
import pysnooper

from aininjas.users.tasks import get_addition
from aininjas.tweetscrape.tasks import task_daily_snap
class Command(BaseCommand):
    help = 'Scrape a Tweet'

    def handle(self, *args, **options):

        task_daily_snap.delay()



