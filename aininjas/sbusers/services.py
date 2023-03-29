from .models import SbUserProfile
from aininjas.contents.models import Prompt, UserDefaultPrompt
import logging
from typing import Tuple, Union
import os
import textwrap

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

logger = logging.getLogger(__name__)

class UsersService():
    def __init__(self):
        pass
    
    def update_user_default_prompt(self, user_profile: SbUserProfile, new_prompt: Prompt) -> Tuple[UserDefaultPrompt, bool]:
        # Prompt.objects.filter(sb_user=user_profile, is_default=True).update(is_default=False)
        result = UserDefaultPrompt.objects.update_or_create(sb_user=user_profile, exec_type=new_prompt.exec_type, defaults={'prompt': new_prompt})
        return result

    def add_default_prompts_for_user(self, sb_user: SbUserProfile, exec_type: str) -> UserDefaultPrompt:
        logger.info(f"Seeding default prompts for user {sb_user}. Grabbing wtv first prompt of type {exec_type}")
        prompt: Union[Prompt, None] = Prompt.objects.filter(sb_user=sb_user, exec_type=exec_type).first()
        if prompt is None:
            # TODO: need to address SEEDING default prompts per user
            if exec_type == Prompt.ExecTypeChoice.DEFAULT_CHUNK_SUMMARIZE:
                prompt = Prompt(
                    name="Default YT Chapter Summarization 1",
                    sb_user=sb_user,
                    prompt=textwrap.dedent("""
                    Prompt: 
                    1. Summarize the unique ideas into bullet points.  Prefix the bullet points with annotation with timestamp in total seconds (seconds)
                    2. Summarize the key lessons into bullet points.  Prefix the bullet points with annotation with timestamp in total seconds (seconds)
                    """).strip(),
                    exec_type=exec_type
                )
                prompt.save()
            elif exec_type == Prompt.ExecTypeChoice.DEFAULT_YT_FINAL_SUMMARIZE:
                print("# seeding FINAL default prompts:")
                prompt = Prompt(
                    name="Default Final Summarization 1",
                    sb_user=sb_user,
                    prompt=textwrap.dedent("""                                   
                    Prompt:
                    1. Write 1 paragraph summarizing everything.
                    2. Group bullet points into categories and annotate with timestamp in total seconds (seconds).
                    """).strip(),
                    exec_type=exec_type
                )         
                prompt.save()
        default_prompt, created = UserDefaultPrompt.objects.update_or_create(sb_user=sb_user, exec_type=prompt.exec_type, defaults={'prompt': prompt})
        logger.info(f"Seeding default prompts for user {sb_user} done")
        return default_prompt
        