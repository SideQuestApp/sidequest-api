from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response
from .models import QuestTree, QuestNode
from rest_framework.permissions import AllowAny
from .serializers import QuestTreeSerializer, QuestNodeSerializer


class GetQuestTrees(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )
    queryset = QuestTree.objects.all()
    serializer_class = QuestTreeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = QuestTreeSerializer(queryset, many=True)

        return Response(serializer.data)


class GetFirstQuestNode(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )
    queryset = QuestNode.objects.all()
    serializer_class = QuestTreeSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('quest_uuid')
        return QuestTree.objects.get(pk=uuid)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        node_query = self.queryset.get(pk=queryset.first_node.pk)
        serializer = QuestNodeSerializer(node_query, many=False)
        return Response(serializer.data)


class GetNextAvailableNodes(generics.ListCreateAPIView):
    permission_classes = (AllowAny, )
    queryset = QuestNode.objects.all()
    serializer_class = QuestNodeSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('node_uuid')
        return QuestNode.objects.get(pk=uuid)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        node_query = queryset.next
        serializer = QuestNodeSerializer(node_query, many=True)
        return Response(serializer.data)


class SetNodeStatus(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    queryset = QuestNode.objects.all()
    serializer_class = QuestNodeSerializer
    status_codes = {
        "NS" : "NotStarted",
        "IP" : "In Progress",
        "F" : "Finished",
        "IC" : "Incomplete"
    }

    def get_queryset(self):
        uuid = self.request.query_params.get('node_uuid')
        return QuestNode.objects.get(pk=uuid)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        node_status = self.request.query_params.get('status')
        if node_status not in self.status_codes:
            return HttpResponse('Bad status code')
        queryset.status = node_status
        queryset.save()
        serializer = QuestNodeSerializer(queryset, many=False)
        return Response(serializer.data)


class SetQuestTreeStatus(generics.GenericAPIView):
    permission_classes = (AllowAny, )
    queryset = QuestTree.objects.all()
    serializer_class = QuestTreeSerializer
    status_codes = {
        "NS" : "NotStarted",
        "IP" : "In Progress",
        "F" : "Finished",
        "IC" : "Incomplete"
    }

    def get_queryset(self):
        uuid = self.request.query_params.get('node_uuid')
        return QuestTree.objects.get(pk=uuid)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        node_status = self.request.query_params.get('status')
        if node_status not in self.status_codes:
            return HttpResponse('Bad status code')
        queryset.status = node_status
        queryset.save()
        serializer = QuestTreeSerializer(queryset, many=False)
        return Response(serializer.data)


class CreateQuest(generics.GenericAPIView):
    """
    """
    pass
    # TODO Call quest generator, take input and make quest
