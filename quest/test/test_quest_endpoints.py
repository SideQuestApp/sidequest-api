from django.test import TestCase
from quest.models import QuestNode, QuestTree
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# ! Wait for the rest of the endpoints before doing anything else
