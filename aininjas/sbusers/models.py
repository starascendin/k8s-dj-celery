from django.db import models
import uuid
from django_extensions.db.models import TimeStampedModel
from fernet_fields import EncryptedTextField

class SbPublicUser(models.Model):
    """
    This pulls from SB's auth.users table
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    email = models.TextField(blank=True)

    class Meta:
        # app_label = 'auth'
        managed = False
        db_table = 'users'

SbPublicUser.objects.using('auth_db')
        
        
class SbUser(models.Model):
    """
    This pulls from sb_users table which gets updated on every auth.users inserts.
    
    This is essentially the Profile for a sbUser
    
    But cannot migrate from DJ since it is not managed by DJ
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    email = models.TextField(blank=True)
    
    class Meta:
        managed = False
        db_table = 'sb_users'
        
        
        
        
class SbUserProfile(models.Model):

    """
    Create a DJ app SB user model.
    Need to create a trigger that inserts from auth.users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.TextField(blank=True, default="", null=True)
    last_name = models.TextField(blank=True, default="", null=True)    
    email = models.CharField(max_length=255, editable=False)
    # openai_key = models.CharField(max_length=255, editable=False)
    openai_key = models.CharField(max_length=255, blank=True, default="", null=True)
    username = models.CharField(max_length=255, default="", null=True)
    avatar_pic = models.CharField(max_length=255, blank=True, default="", null=True)
    # TODO: implement encryption for below
    chatgpt_plus_username = models.CharField(max_length=255, blank=True, default="", null=True)
    chatgpt_plus_password = EncryptedTextField(blank=True, default="", null=True)

    class Meta:
        db_table = 'sb_users_profile'
