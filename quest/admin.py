from django.contrib import admin
from .models import QuestNode, QuestTree, QuestReviews, LangChainVars
admin.site.register(QuestTree)
admin.site.register(QuestNode)
admin.site.register(QuestReviews)
admin.site.register(LangChainVars)
