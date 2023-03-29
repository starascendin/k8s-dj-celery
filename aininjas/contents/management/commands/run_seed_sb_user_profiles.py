from django.core.management.base import BaseCommand, CommandError
from aininjas.contents.models import ContentSource, ContentProcessed, Prompt
from aininjas.contents.services import ContentService, ContentPromptOrchestrator, PromptService

from config.settings.base import YT_API_KEY
from scripts.libs.yt_transcript_client import YtClient
from aininjas.sbusers.models import SbPublicUser, SbUserProfile

import textwrap
import snoop


class Command(BaseCommand):
    help = "Seed hardcoded prompts"

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)
    @snoop
    def handle(self, *args, **options):
        """
        Take all sb auth.users, copy to sb_users_profile
        """
        
        all_auth_users = SbPublicUser.objects.all()
        user_profiles = []
        for sb_auth_user in all_auth_users:
            print("# sb_auth_user", sb_auth_user)
            user_profiles.append(SbUserProfile(
                id=sb_auth_user.id,
                email=sb_auth_user.email,
            ))
        
        x = SbUserProfile.objects.bulk_create(user_profiles, ignore_conflicts=True)