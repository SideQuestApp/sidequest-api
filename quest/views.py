import json
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
        uuid = self.request.query_params.get('tree_uuid')
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
    # TODO Optimize this better
    permission_classes = (AllowAny, )
    queryset = QuestTree.objects.all()

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        quest_tree = QuestTree.objects.create(
            name=body['mainQuest']["title"],
            description=body['mainQuest']["description"],
            status="NS",
            completion_exp=1000,
            price_low=100,
            price_high=200
        )
        uuid_map = {}
        # ! Remember to adjust for when values are dynamic
        for quest in body["mainQuest"]["miniQuests"]:
            quest_node = QuestNode.objects.create(
                name=quest["title"],
                description=quest["description"],
                longitude=quest["longitude"],
                latitude=quest["latitude"],
                price_low=10,
                price_high=25,
                completion_experience=100,
                quest=quest_tree
            )
            uuid_map[quest["uuid"]] = quest_node
            if quest["uuid"] == "2":
                quest_tree.first_node = quest_node
                quest_tree.save()

        quest_tree.last_node = quest_node
        quest_tree.save()

        for sequence in body["questSequence"]:
            current_node = uuid_map[sequence["prev"]]
            for next_node in sequence["next"]:
                current_node.next.add(uuid_map[next_node])
                current_node.save()
        return HttpResponse('Created a new quest without error')

    # TODO Call quest generator, take input and make quest
