from django.test import TestCase
from quest.models import LocationReviews


class LocationReviewsTestCase(TestCase):
    def setUp(self):
        LocationReviews.objects.create(
            quest='testquest',
            user='testuser',
            score=5,
            chain='testchain',
            latitude=42.736979,
            longitude=-84.483865,
            location_name='testLocation'
        )
