from django.urls import path, include
from quest import views

app_name = 'quests'

urlpatterns = [
    path('quest_trees/', view=views.GetQuestTrees.as_view(), name='get_nodes'),
    path('quest_trees/first_node/', view=views.GetFirstQuestNode.as_view(), name='get_first_node'),
    path('quest_trees/next_node/', view=views.GetNextAvailableNodes.as_view(), name='get_next_nodes'),
    path('quest_trees/node_status_change/', view=views.SetNodeStatus.as_view(), name='change_node_status'),
    path('quest_trees/tree_status_change/', view=views.SetQuestTreeStatus.as_view(), name='change_tree_status'),
    path('quest_trees/create_quest/', view=views.CreateQuest.as_view(), name='create_quest'),
]
