from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from .models import QuestTree, QuestMap, QuestNode, NodeRelation
from rest_framework.permissions import AllowAny


class GetQuestNodes(generics.CreateAPIView):
    permission_classes = (AllowAny, )
    queryset = QuestTree.objects.all()

    def get(self, request, *args, **kwargs):
        quest_uuid = request.query_params.get('quest_id')
        quest = QuestTree.objects.get(pk=quest_uuid)

        relation_table = QuestMap.objects.get(pk=quest.relations.pk)

        node_relations = NodeRelation.objects.filter(relations_map=relation_table)

        return HttpResponse(node_relations)
