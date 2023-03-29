

from ninja_extra import NinjaExtraAPI, api_controller, http_get
from ninja import Router
from ninja import Schema
from aininjas.sbusers.models import SbPublicUser, SbUserProfile
from aininjas.contents.models import UserDefaultPrompt, Prompt
from .services import UsersService
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from ninja.errors import HttpError
router = Router()


class SetDefaultUserPromptIn(Schema):
    prompt_id: str

user_service = UsersService()

@router.get('/ping', auth=None)
def ping(request):

    return "PONG!"

# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# @router.get('/gauth', auth=None)
# def gauth(request):

#     return "PONG!"

@router.post('/set-default-prompt')
def set_default_user_prompt(request, set_default_prompt_in: SetDefaultUserPromptIn):
    user = request.auth
    prompt = Prompt.objects.get(id=set_default_prompt_in.prompt_id)
    result, created = user_service.update_user_default_prompt(user, prompt)
    print("#DEBUG UPdated defautl result, created ", result, created)
    return 'DONE!'
