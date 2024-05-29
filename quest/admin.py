from django.contrib import admin
from .models import QuestNode, QuestTree
admin.site.register(QuestTree)
admin.site.register(QuestNode)
