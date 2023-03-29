from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from django_extensions.db.models import TimeStampedModel

# Create your models here.

class TweetDailySnap(TimeStampedModel):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  
  # should have search query params + Daily snaps
  query_params = models.CharField(max_length=255, unique=True)
  daily_snap = models.TextField(blank=True)
