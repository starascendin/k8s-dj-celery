import pytest
from aininjas.sbusers.models import SbUserProfile
from aininjas.sbusers.services import UsersService
from aininjas.contents.models import Prompt, UserDefaultPrompt
from typing import Tuple, Union


@pytest.mark.django_db
def test_update_user_default_prompt():
    # Create a test user and user profile
    user_profile = SbUserProfile.objects.create(email="test_1234@gmail.com")
    user_service = UsersService()

    # Create two prompts for DEFAULT_CHUNK_SUMMARIZE for the test user
    prompt_1 = Prompt.objects.create(sb_user=user_profile, name='Prompt 1', prompt='Sample prompt 1', exec_type='DEFAULT_CHUNK_SUMMARIZE')
    prompt_2 = Prompt.objects.create(sb_user=user_profile, name='Prompt 2', prompt='Sample prompt 2', exec_type='DEFAULT_CHUNK_SUMMARIZE')

    # Call the update_user_default_prompt function
    result, created = user_service.update_user_default_prompt(user_profile, prompt_1)
    assert created == True
    assert result.prompt == prompt_1

    result, created = user_service.update_user_default_prompt(user_profile, prompt_2)
    assert created == False
    assert result.prompt == prompt_2
    
    list = UserDefaultPrompt.objects.filter(sb_user=user_profile, exec_type='DEFAULT_CHUNK_SUMMARIZE')
    assert len(list) == 1
    assert list[0].prompt == prompt_2


    # Create two prompts for DEFAULT_CHUNK_SUMMARIZE for the test user
    final_prompt_1 = Prompt.objects.create(sb_user=user_profile, name='Prompt 1', prompt='Sample prompt 1', exec_type='DEFAULT_YT_FINAL_SUMMARIZE')
    final_prompt_2 = Prompt.objects.create(sb_user=user_profile, name='Prompt 2', prompt='Sample prompt 2', exec_type='DEFAULT_YT_FINAL_SUMMARIZE')

    # Call the update_user_default_prompt function
    result, created = user_service.update_user_default_prompt(user_profile, final_prompt_1)
    assert created == True
    assert result.prompt == final_prompt_1

    result, created = user_service.update_user_default_prompt(user_profile, final_prompt_2)
    assert created == False
    assert result.prompt == final_prompt_2
    
    list = UserDefaultPrompt.objects.filter(sb_user=user_profile, exec_type='DEFAULT_YT_FINAL_SUMMARIZE')
    assert len(list) == 1
    assert list[0].prompt == final_prompt_2
    
    user_defaults = UserDefaultPrompt.objects.filter(sb_user=user_profile)
    assert len(user_defaults) == 2
    assert user_defaults[0].prompt == prompt_2
    assert user_defaults[0].exec_type == 'DEFAULT_CHUNK_SUMMARIZE'
    assert user_defaults[1].prompt == final_prompt_2
    assert user_defaults[1].exec_type == 'DEFAULT_YT_FINAL_SUMMARIZE'


    # # Test updating to a non-existent prompt
    # with pytest.raises(ValueError):
    #     update_user_default_prompt(user_profile, "non_existent_id")