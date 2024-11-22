from django.urls import path, include
from quest import views
from profiles import views as views_profile

app_name = 'quests'

urlpatterns = [
    path('quest_trees/first_node/', view=views.GetFirstQuestNode.as_view(), name='get_first_node'),
    path('quest_trees/next_node/', view=views.GetNextAvailableNodes.as_view(), name='get_next_nodes'),
    path('quest_trees/node_status_change/', view=views.SetNodeStatus.as_view(), name='change_node_status'),
    path('quest_trees/tree_status_change/', view=views.SetQuestTreeStatus.as_view(), name='change_tree_status'),
    path('quest_trees/create_quest/', view=views.CreateQuest.as_view(), name='create_quest'),
    path('quest_trees/get_quest_tree/', view=views.GetQuestTree.as_view(), name='get_quest'),
    path('wouldyourather/create/', view=views_profile.CreateWouldYouRatherQA.as_view(), name='create_qa'),
    path('wouldyourather/answer/', view=views_profile.AnswerWouldYouRatherQA.as_view(), name='answer_qa'),
    path('wouldyourather/', view=views_profile.GetWouldYouRatherQA.as_view(), name='get_qa'),
    path('quest_trees/review/create', view=views.ReviewQuest.as_view(), name='review_quest'),
    path('quest_trees/review/get', view=views.GetReviews.as_view(), name='get_quest_reviews'),
    path('quest_trees/location_review/add', view=views.ReviewLocation.as_view(), name='review_location'),
    path('quest_trees/location_review/get', view=views.GetLocationReviews.as_view(), name='get_location_reviews')
]
