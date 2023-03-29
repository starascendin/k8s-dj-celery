from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django_extensions.db.models import TimeStampedModel
import hashlib
# from aininjas.sbusers.models import SbUser

# # BL: A hack to bring SbUser into model is by re-defining it at the model app level.
# class SbUsersUser(models.Model):
#     """
#     This pulls from SB's auth.users table
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     aud = models.CharField(max_length=255, editable=False)
#     role = models.CharField(max_length=255, editable=False)
#     email = models.CharField(max_length=255, editable=False)

#     class Meta:
#         # app_label = 'auth'
#         managed = False
#         db_table = 'auth\".\"users'



class User(AbstractUser):
    """
    Default custom user model for aininjas.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    # sb_user = models.ForeignKey(SbUsersUser, on_delete=models.CASCADE, blank=True, null=True)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})




