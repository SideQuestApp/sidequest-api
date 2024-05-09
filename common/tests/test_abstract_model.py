import uuid
from django.test import TestCase
from ..models import TestUuid


class MyModelTestCase(TestCase):
    """
    * Test if the new created models have unique uuid
    """
    def test_uuid_creation(self):
        my_model_instance = TestUuid.objects.create(name="TestName")
        another_instance = TestUuid.objects.create(name="TestName2")

        self.assertIsInstance(my_model_instance.id, uuid.UUID)
        self.assertNotEqual(my_model_instance.id, another_instance.id)
