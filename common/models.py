from django.db import models
import uuid


class AbstractBaseModel(models.Model):
    """
    * Overrides the default model of django
    * It replaces id for auto increment integer to uuid
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ["-datetime_created"]


class TestUuid(AbstractBaseModel):
    """
    * This model is used only to test if models generate uuid instead of integer
    * This model test gh test actions
    """
    name = models.CharField(max_length=10)
