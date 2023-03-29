import factory
import uuid
from aininjas.sbusers.models import SbUserProfile

class SbUserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SbUserProfile

    id = factory.LazyFunction(uuid.uuid4)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    openai_key = factory.Faker('uuid4')
    username = factory.Faker('user_name')
    avatar_pic = factory.Faker('image_url')
    chatgpt_plus_username = factory.Faker('user_name')
    chatgpt_plus_password = factory.Faker('password')
