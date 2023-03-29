from ninja import NinjaAPI, Form
from ninja.security import HttpBearer
from aininjas.sbusers.models import SbUserProfile
from config.settings.base import YT_API_KEY, SUPABASE_KEY, SUPABASE_URL, ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from supabase.client import create_client
import logging
logger = logging.getLogger(__name__)
import snoop
from ninja.errors import HttpError


# https://django-ninja.rest-framework.com/guides/authentication/
# BL: I prob need to add this to global. Then proxy every request to supabase

class GlobalAuth(HttpBearer):
    @snoop
    def authenticate(self, request, key):
        authorization_header = request.headers.get("Authorization") or None
        if not authorization_header:
            raise HttpError(400, "Authorization header is required")
        jwt_token = authorization_header.split(" ")[1]
        sb = create_client(
            SUPABASE_URL, 
            SUPABASE_KEY, 
            )
        postgrest_client = sb.postgrest
        postgrest_client.auth(jwt_token)
        try:
            resp = sb.from_('sb_users_profile').select('*').execute()
            if len(resp.data) == 0:
                return None
            user_id = resp.data[0]['id']
            if not user_id:
                return None
            print("")
            sb_user = SbUserProfile.objects.get(id=user_id)
            return sb_user
        except Exception as e:
            logger.warn(f"Auth Token Error: {e}")
            return 
        
        