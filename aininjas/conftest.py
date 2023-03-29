import pytest

from aininjas.users.models import User
from aininjas.users.tests.factories import UserFactory
from django.conf import settings
from config.settings.base import DATABASES

@pytest.fixture(scope='session')
def django_db_setup():
    settings.DATABASES = DATABASES.copy()

@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


