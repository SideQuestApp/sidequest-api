from django.contrib import admin
from .models import QuestNode, QuestMap, QuestTree, NodeRelation
admin.site.register(QuestTree)
admin.site.register(QuestNode)
admin.site.register(QuestMap)
admin.site.register(NodeRelation)
