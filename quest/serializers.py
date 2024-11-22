from .models import QuestTree, QuestNode, QuestReviews, LocationReviews
from rest_framework import serializers


class QuestTreeSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = QuestTree
        fields = [
            'pk',
            'location',
            'name',
            'description',
            'status',
            'completion_exp',
            'price_low',
            'price_high'
        ]


class QuestNodeSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = QuestNode
        fields = [
            'pk',
            'name',
            'description',
            'longitude',
            'latitude',
            'status',
            'price_low',
            'price_high',
            'optional',
            'completion_experience'
        ]


class QuestReviewSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = QuestReviews
        fields = [
            'pk',
            'quest',
            'chain',
            'user',
            'score'
        ]


class LocationReviewSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = LocationReviews
        fields = [
            'pk'
            'quest'
            'user'
            'score'
            'chain'
            'latitude'
            'longitude'
            'location_name'
        ]
