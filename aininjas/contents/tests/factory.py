import factory
import uuid
from aininjas.contents.models import ContentCreator, ContentSource, ContentProcessed, ContentYtChunk, Prompt, PromptCompletion, UserDefaultPrompt, UserPromptRunVersion, PromptCompletionExecutionHistory
from aininjas.sbusers.models import SbPublicUser, SbUserProfile
from aininjas.sbusers.tests.factory import SbUserProfileFactory


class ContentCreatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentCreator

    id = factory.LazyFunction(uuid.uuid4)
    creator_name = factory.Faker('name')
    creator_id = factory.Faker('uuid4')
    creator_url = factory.Faker('url')
    profile_json_blob = factory.LazyFunction(lambda: {})
    source_channel = factory.Iterator(ContentCreator.SourceChoice.choices, getter=lambda c: c[0])


class ContentSourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentSource

    id = factory.LazyFunction(uuid.uuid4)
    url = factory.Faker('url')
    content_creator = factory.SubFactory(ContentCreatorFactory)
    content_title = factory.Faker('sentence')
    content_description = factory.Faker('text')
    content_categories = factory.Iterator(ContentSource.TopicCategoryChoice.choices, getter=lambda c: c[0])
    raw_content_json_blob = factory.LazyFunction(lambda: {})
    content_meta_json = factory.LazyFunction(lambda: {})
    param_json_blob = factory.LazyFunction(lambda: {})
    speaker_type = factory.Iterator(ContentSource.SpeakerTypeChoice.choices, getter=lambda c: c[0])
    number_of_speaker = factory.Faker('random_int', min=1, max=5)
    speakers_blob = factory.LazyFunction(lambda: {})


class ContentProcessedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentProcessed

    id = factory.LazyFunction(uuid.uuid4)
    content = factory.SubFactory(ContentSourceFactory)
    number_of_speaker = factory.Faker('random_int', min=1, max=5)
    processing_algo_type = factory.Iterator(ContentProcessed.ProcessAlgoTypeChoice.choices, getter=lambda c: c[0])
    processed_content_json_blob = factory.LazyFunction(lambda: {})
    state = factory.Iterator(ContentProcessed.ProcessStateChoice.choices, getter=lambda c: c[0])
    state_artifact_blob = factory.LazyFunction(lambda: {})
    is_chunked = factory.Faker('boolean')
    output_artifacts_url = factory.Faker('url')
    time_to_process = factory.LazyFunction(lambda: {})


class ContentYtChunkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContentYtChunk

    id = factory.LazyFunction(uuid.uuid4)
    content_processed = factory.SubFactory(ContentProcessedFactory)
    transcript_start_time = factory.Faker('random_int')
    content_chunk_title = factory.Faker('sentence')
    content_chunk_text = factory.Faker('text')
    content_segments_json = factory.LazyFunction(lambda: {})
    raw_data_json_blob = factory.LazyFunction(lambda: {})


class PromptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Prompt

    id = factory.LazyFunction(uuid.uuid4)
    sb_user = factory.SubFactory(SbUserProfileFactory)
    name = factory.Faker('word')
    prompt = factory.Faker('text')
    categories = factory.Iterator(Prompt.PromptCategoryChoice.choices, getter=lambda c: c[0])
    exec_type = factory.Iterator(Prompt.ExecTypeChoice.choices, getter=lambda c: c[0])


# class PromptCompletionFactory(factory.django.D
class PromptCompletionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PromptCompletion
    id = factory.LazyFunction(uuid.uuid4)
    content_chunk = factory.SubFactory(ContentYtChunkFactory)
    content_processed = factory.SubFactory(ContentProcessedFactory)
    prompt = factory.SubFactory(PromptFactory)
    prompt_text = factory.Faker('text')
    prompt_hashed = factory.Faker('uuid4')
    completion_state = factory.Iterator(PromptCompletion.CompletionStateChoice.choices, getter=lambda c: c[0])
    output_completion = factory.Faker('text')
    sb_user = factory.SubFactory(SbUserProfileFactory)



class UserDefaultPromptFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserDefaultPrompt
    id = factory.LazyFunction(uuid.uuid4)
    sb_user = factory.SubFactory(SbUserProfileFactory)
    prompt = factory.SubFactory(PromptFactory)
    exec_type = factory.Iterator(Prompt.ExecTypeChoice.choices, getter=lambda c: c[0])


class UserPromptRunVersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserPromptRunVersion
    id = factory.LazyFunction(uuid.uuid4)
    sb_user = factory.SubFactory(SbUserProfileFactory)
    processed = factory.SubFactory(ContentProcessedFactory)
    run_type = factory.Iterator(UserPromptRunVersion.PromptRunTypeChoice.choices, getter=lambda c: c[0])

class PromptCompletionExecutionHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PromptCompletionExecutionHistory

    id = factory.LazyFunction(uuid.uuid4)
    user_processed_prompt_version = factory.SubFactory(UserPromptRunVersionFactory)
    source_content_processed = factory.SubFactory(ContentProcessedFactory)
    source_content_chunk = factory.SubFactory(ContentYtChunkFactory)
    prompt_completion = factory.SubFactory(PromptCompletionFactory)
