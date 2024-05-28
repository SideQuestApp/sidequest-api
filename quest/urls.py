from django.urls import path, include
from quest import views

urlpatterns = [
    path('quest/', view=views.GetQuestNodes.as_view(), name='get_nodes')
]
