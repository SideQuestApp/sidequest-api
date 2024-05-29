from django.urls import path, include
from quest import views

urlpatterns = [
    path('quest_trees/', view=views.GetQuestTrees.as_view(), name='get_nodes'),
    path('quest_trees/first_node/', view=views.GetFirstQuestNode.as_view(), name='get_first_node')
]
