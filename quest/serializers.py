from .models import QuestTree, QuestNode
from rest_framework import serializers


class QuestTreeSerializer(serializers.ModelSerializer):
    """
    """
    class Meta:
        model = QuestTree
        fields = [
            'pk',
            'name',
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
