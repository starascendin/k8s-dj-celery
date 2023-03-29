from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django_extensions.db.models import TimeStampedModel
import hashlib
from aininjas.sbusers.models import SbPublicUser, SbUserProfile



class ContentCreator(TimeStampedModel):
  class SourceChoice(models.TextChoices):
    NONE = 'NONE', _('NONE')
    TWITTER = 'TWITTER', _('TWITTER')
    YOUTUBE = 'YOUTUBE', _('YOUTUBE')
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  creator_name = models.CharField(max_length=255, blank=True)
  creator_id = models.CharField(max_length=255, unique=True)
  creator_url = models.CharField(max_length=255, blank=True)
  profile_json_blob = models.JSONField(default=dict, blank=True)
  source_channel = models.CharField(
    max_length=50,
    choices=SourceChoice.choices,
    default=SourceChoice.NONE
  )

class ContentSource(TimeStampedModel):
    class SourceChoice(models.TextChoices):
        NONE = 'NONE', _('NONE')
        TWITTER = 'TWITTER', _('TWITTER')
        YOUTUBE = 'YOUTUBE', _('YOUTUBE')

    class TopicCategoryChoice(models.TextChoices):
        NONE = 'NONE', _('NONE')
        GPT = 'GPT', _('GPT')
        CRYPTO = 'CRYPTO', _('CRYPTO')
    class SpeakerTypeChoice(models.TextChoices):
      NONE = 'NONE', _('NONE')
      MONO = 'MONO', _('MONO') # for mono
      DUO = 'DUO', _('DUO') # for 2 speakers
      MULTI = 'MULTI', _('MULTI') # for 3+ speakers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.CharField(max_length=255, blank=True, unique=True)
    content_creator = models.ForeignKey(ContentCreator, on_delete=models.CASCADE)
    content_title = models.CharField(max_length=255, blank=True)
    content_description = models.TextField(blank=True)
    content_categories = models.CharField(
      max_length=50,
      choices=TopicCategoryChoice.choices,
      default=TopicCategoryChoice.NONE
    )
    raw_content_json_blob = models.JSONField(default=dict, blank=True)
    content_meta_json = models.JSONField(default=dict, blank=True)
    param_json_blob = models.JSONField(default=dict, blank=True)
    speaker_type = models.CharField(
      max_length=50,
      choices=SpeakerTypeChoice.choices,
      default=SpeakerTypeChoice.MONO
    )
    number_of_speaker = models.IntegerField(default=1)
    speakers_blob = models.JSONField(default=dict, blank=True)
    # # TODO define a pydantic model for json blob
    # processed_content_json_blob = models.JSONField(default=dict, blank=True)

    class Meta:
      indexes = [
            models.Index(fields=['url',]),
      ]
    def __str__(self):
        return str(self.id)


# BL: ContentProcessed should be a job
class ContentProcessed(TimeStampedModel):
    class ProcessAlgoTypeChoice(models.TextChoices):
      NONE = 'NONE', _('NONE')
      NORMAL_YT_TRANSCRIBE = 'NORMAL_YT_TRANSCRIBE', _('NORMAL_YT_TRANSCRIBE') # for mono
      SPEAKER_TRANSCRIBE = 'SPEAKER_TRANSCRIBE', _('SPEAKER_TRANSCRIBE') # for 2+ speakers

    class ProcessStateChoice(models.TextChoices):
        """
        None
        WAV_EXTRACTED
        WAV_STORED
        TRANSCRIPT_STORED
        COMPLETED
        """
        NONE = 'NONE', _('NONE')
        ERROR = 'ERROR', _('ERROR')
        WAV_JOB_STARTED = 'WAV_JOB_STARTED', _('WAV_JOB_STARTED')
        WAV_STORED = 'WAV_STORED', _('WAV_STORED')
        TRANSCRIPT_STORED = 'TRANSCRIPT_STORED', _('TRANSCRIPT_STORED')
        READY_TO_CHUNK = 'READY_TO_CHUNK', _('READY_TO_CHUNK')
        COMPLETED = 'COMPLETED', _('COMPLETED')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(ContentSource, on_delete=models.CASCADE)
    number_of_speaker = models.IntegerField(default=1)
    processing_algo_type = models.CharField(
      max_length=50,
      choices=ProcessAlgoTypeChoice.choices,
      default=ProcessAlgoTypeChoice.NONE
    )
    # this is the final processed/formatted output
    processed_content_json_blob = models.JSONField(default=dict, blank=True)
    state = models.CharField(
      max_length=255,
      choices=ProcessStateChoice.choices,
      default=ProcessStateChoice.NONE
    )
    # for state transition artifacts
    state_artifact_blob = models.JSONField(default=dict, blank=True)

    # This is to prevent re-chunking. What about if you want to re-run with diff chunk algo?
    is_chunked = models.BooleanField(default=False)
    # final output artifact
    output_artifacts_url = models.CharField(max_length=255,blank=True)
    time_to_process = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return str(self.id)


class ContentYtChunk(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_processed = models.ForeignKey(ContentProcessed, on_delete=models.CASCADE, related_name='content_chunks')
    transcript_start_time = models.IntegerField(default=-1)
    content_chunk_title = models.TextField(blank=True)
    content_chunk_text = models.TextField(blank=True)
    content_segments_json = models.JSONField(default=dict, blank=True)
    raw_data_json_blob = models.JSONField(default=dict, blank=True)

    class Meta:
      indexes = [
            models.Index(fields=['content_processed', 'transcript_start_time']),
      ]
      unique_together = ('content_processed', 'transcript_start_time')

    def __str__(self):
        return str(f'{self.id} - {self.transcript_start_time} - {self.content_chunk_title}')




# === PROMPT RELATED MODELS ===
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django_extensions.db.models import TimeStampedModel

from aininjas.contents.models import ContentYtChunk
# Create your models here.

# ======= PROMPTS =========
# These should be stand alone

class Prompt(TimeStampedModel):
    class PromptCategoryChoice(models.TextChoices):
        NONE = 'NONE', _('NONE')
        SUMMARIZATION = 'SUMMARIZATION', _('SUMMARIZATION')
    class ExecTypeChoice(models.TextChoices):
        NONE = 'NONE', _('NONE')
        DEFAULT_CHUNK_SUMMARIZE = 'DEFAULT_CHUNK_SUMMARIZE', _('DEFAULT_CHUNK_SUMMARIZE')
        DEFAULT_YT_FINAL_SUMMARIZE = 'DEFAULT_YT_FINAL_SUMMARIZE', _('DEFAULT_YT_FINAL_SUMMARIZE')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sb_user = models.ForeignKey(SbUserProfile, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    prompt = models.TextField(blank=True)

    categories = models.CharField(
      max_length=50,
      choices=PromptCategoryChoice.choices,
      default=PromptCategoryChoice.NONE
    )
    exec_type = models.CharField(
      max_length=50,
      choices=ExecTypeChoice.choices,
      default=ExecTypeChoice.NONE
    )


    def __str__(self):
        return str(f'{self.id} - {self.name}')

class PromptCompletion(TimeStampedModel):
    class CompletionStateChoice(models.TextChoices):
        NONE = 'NONE', _('NONE')
        COMPLETED = 'COMPLETED', _('COMPLETED')
        FAILED = 'FAILED', _('FAILED')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_chunk = models.ForeignKey(ContentYtChunk, on_delete=models.SET_NULL, blank=True, null=True)
    content_processed = models.ForeignKey(ContentProcessed, on_delete=models.SET_NULL, blank=True, null=True)
    prompt = models.ForeignKey(Prompt, on_delete=models.SET_NULL, blank=True, null=True)
    prompt_text = models.TextField(blank=True)
    prompt_hashed = models.CharField(max_length=255, blank=True)
    completion_state = models.CharField(
      max_length=255,
      choices=CompletionStateChoice.choices,
      default=CompletionStateChoice.NONE
    )
    output_completion = models.TextField(blank=True)
    sb_user = models.ForeignKey(SbUserProfile, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class UserDefaultPrompt(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sb_user = models.ForeignKey(SbUserProfile, on_delete=models.SET_NULL, blank=True, null=True)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, blank=True, null=True)
    exec_type = models.CharField(
      max_length=50,
      choices=Prompt.ExecTypeChoice.choices,
      default=Prompt.ExecTypeChoice.NONE
    )


    class Meta:
      unique_together = ('sb_user', 'exec_type')


    def __str__(self):
        return str(self.id)

# ==== Sb Auth User + RunHistory + RunPC History ====

## UserRunVersionHistory
class UserPromptRunVersion(TimeStampedModel):
  class PromptRunTypeChoice(models.TextChoices):
      NONE = 'NONE', _('NONE')
      YT_CHUNK_SUMMARIZE = 'YT_CHUNK_SUMMARIZE', _('YT_CHUNK_SUMMARIZE')
      YT_FINAL_SUMMARIZE = 'YT_FINAL_SUMMARIZE', _('YT_FINAL_SUMMARIZE')
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  sb_user = models.ForeignKey(SbUserProfile, on_delete=models.SET_NULL, blank=True, null=True)
  processed = models.ForeignKey(ContentProcessed, on_delete=models.SET_NULL, blank=True, null=True)
  run_type = models.CharField(
      max_length=255,
      choices=PromptRunTypeChoice.choices,
      default=PromptRunTypeChoice.NONE
    )


  # class Meta:
  #   unique_together = ('sb_user', 'processed', 'run_version', 'run_type')

## PromptCompletionExecutionHistory
class PromptCompletionExecutionHistory(TimeStampedModel):
  """
  This will hold all things PC with any related data, which can be: Processed, Chunks, version, etc
  PromptCompletionExecution can be 1 off, or from a group which is a 1 off.

  This is just dump of PromptCompletionExecution from whatever upstream source
  """
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  user_processed_prompt_version = models.ForeignKey(UserPromptRunVersion, on_delete=models.SET_NULL, blank=True, null=True)
  source_content_processed = models.ForeignKey(ContentProcessed, on_delete=models.SET_NULL, blank=True, null=True)
  source_content_chunk = models.ForeignKey(ContentYtChunk, on_delete=models.SET_NULL, blank=True, null=True)
  prompt_completion = models.ForeignKey(PromptCompletion, on_delete=models.CASCADE)

