import json
import ast
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import generics, status
from rest_framework.response import Response
from .models import QuestTree, QuestNode, QuestReviews
from rest_framework.permissions import AllowAny
from .serializers import QuestTreeSerializer, QuestNodeSerializer, QuestReviewSerializer
import profiles
from django.shortcuts import get_object_or_404
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class GetQuestTree(generics.ListCreateAPIView):
    """
    * Gets the Quest Tree.
    * You are able to query using any of the Quest Tree field.
    """
    permission_classes = (AllowAny, )
    queryset = QuestTree.objects.all()
    serializer_class = QuestTreeSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('quest_uuid')
        if uuid:
            return get_object_or_404(QuestTree, pk=uuid)

        filter_kwargs = {}
        for key, value in self.request.query_params.items():
            if hasattr(QuestTree, key):
                filter_kwargs[key] = value

        if filter_kwargs:
            return QuestTree.objects.filter(**filter_kwargs)
        else:
            return QuestTree.objects.all()

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        serializer = QuestTreeSerializer(queryset if queryset else self.queryset.all(),
                                         many=False if request.query_params.get('quest_uuid')
                                         else True)

        return Response(serializer.data)


class GetFirstQuestNode(generics.ListCreateAPIView):
    """
    * Gets the first QuestNode of a given QuestTree
    * Quury using the QuestTree pk
    """
    permission_classes = (AllowAny, )
    queryset = QuestNode.objects.all()
    serializer_class = QuestTreeSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('quest_uuid')
        return get_object_or_404(QuestTree, pk=uuid)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        node_query = self.queryset.get(pk=queryset.first_node.pk)
        serializer = QuestNodeSerializer(node_query, many=False)
        return Response(serializer.data)


class GetNextAvailableNodes(generics.ListCreateAPIView):
    """
    * Gets the next QuestNodes of a given QuestNode
    * Query using the QuestNode pk
    """
    permission_classes = (AllowAny, )
    queryset = QuestNode.objects.all()
    serializer_class = QuestNodeSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('node_uuid')

        return get_object_or_404(QuestNode, pk=uuid)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset:
            node_query = queryset.next
            serializer = QuestNodeSerializer(node_query, many=True)
            return Response(serializer.data)
        else:
            return Response('No matching nodes')


class SetNodeStatus(generics.GenericAPIView):
    """
    * Sets the activity status of a QuestNode
    * Query using the QuestNode pk
    * Status must be one of possible statuses:

        "NS" : "NotStarted",

        "IP" : "In Progress",

        "F" : "Finished",

        "IC" : "Incomplete"
    """

    permission_classes = (AllowAny, )
    queryset = QuestNode.objects.all()
    serializer_class = QuestNodeSerializer

    status_codes = {
        "NS" : "NotStarted",
        "IP" : "In Progress",
        "F" : "Finished",
        "IC" : "Incomplete"
    }

    def get_queryset(self, node):
        uuid = self.request.query_params.get('node_uuid')

        return get_object_or_404(QuestNode, pk=uuid)

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
    """
    * Sets the activity status of a QuestTree
    * Query using the QuestTree pk
    * Status must be one of possible statuses:

        "NS" : "NotStarted",

        "IP" : "In Progress",

        "F" : "Finished",

        "IC" : "Incomplete"
    """

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
        return get_object_or_404(QuestTree, pk=uuid)

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
    * Creates a questree with a start and end node
    * Quest is created using LangChain request
    """
    permission_classes = (AllowAny, )
    queryset = QuestTree.objects.all()

    def get_queryset(self, body):
        return get_object_or_404(profiles.models.User, pk=body['user_pk'])

    def post(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        # TODO Include Would you rather questions in the body of the call
        # TODO Longterm Goal is to include location and call different documents for RAG depending on it

        body = json.loads(body_unicode)
        user = self.get_queryset(body)

        # Quest generation using langchain
        # !Need a func to asing a default chain to user
        model = ChatOpenAI(model=user.chain.model)
        messages = [
            SystemMessage(content=user.chain.system_prompt),
            HumanMessage(content=body["location"]),
        ]
        response = model.invoke(messages)
        response_json = ast.literal_eval(response.content)

        quest_tree = QuestTree.objects.create(
            name=response_json['mainQuest']["title"],
            description=response_json['mainQuest']["description"],
            location=body["location"],
            status="NS",
            completion_exp=1000,
            price_low=100,
            price_high=200,
            chain=user.chain,
            length=response_json['mainQuest']["length"]
        )
        uuid_map = {}
        # ! Remember to adjust for when values are dynamic

        starting_quest = response_json['mainQuest']["startQuest"]

        starting_node = QuestNode.objects.create(
            name=starting_quest["title"],
            description=starting_quest["description"],
            longitude=starting_quest["longitude"],
            latitude=starting_quest["latitude"],
            status='IP',
            price_low=10,
            price_high=25,
            completion_experience=100,
            quest=quest_tree,
            chain=user.chain
        )
        quest_tree.first_node = starting_node
        uuid_map[2] = starting_node
        quest_tree.save()

        ending_quest = response_json['mainQuest']["endQuest"]

        ending_node = QuestNode.objects.create(
            name=ending_quest["title"],
            description=ending_quest["description"],
            longitude=ending_quest["longitude"],
            latitude=ending_quest["latitude"],
            status='NS',
            price_low=10,
            price_high=25,
            completion_experience=100,
            quest=quest_tree,
            chain=user.chain
        )
        quest_tree.last_node = ending_node
        uuid_map[quest_tree.length + 1] = ending_node
        quest_tree.save()

        # TODO: add sequence to the quest tree starting creation

        return HttpResponse('Created a new quest without error')


class ReviewQuest(generics.GenericAPIView):
    """
    * User reviews of quests
    """
    permission_classes = (AllowAny, )
    queryset = QuestReviews.objects.all()
    serializer_class = QuestReviewSerializer

    def get_queryset(self, pk, model):
        return get_object_or_404(model, pk=pk)

    def post(self, request, *args, **kwargs):
        # TODO: Create a function for loading in the body
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        user = self.get_queryset(body['user_pk'], profiles.models.User)
        quest = self.get_queryset(body['quest_pk'], QuestTree)
        score = body['score']
        review = QuestReviews.objects.create(
            quest=quest,
            user=user,
            chain=user.chain,
            score=score
        )
        serializer = QuestReviewSerializer(review, many=False)
        return Response(serializer.data)


class GetReviews(generics.ListCreateAPIView):
    """"""
    permission_classes = (AllowAny, )
    queryset = QuestReviews.objects.all()
    serializer_class = QuestReviewSerializer

    def get_queryset(self):
        uuid = self.request.query_params.get('review_uuid')
        if uuid:
            return get_object_or_404(QuestReviews, pk=uuid)

        filter_kwargs = {}
        for key, value in self.request.query_params.items():
            if hasattr(QuestReviews, key):
                filter_kwargs[key] = value

        if filter_kwargs:
            return QuestReviews.objects.filter(**filter_kwargs)
        else:
            return QuestReviews.objects.all()

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        serializer = QuestReviewSerializer(queryset if queryset else self.queryset.all(),
                                           many=False if request.query_params.get('review_uuid')
                                           else True)

        return Response(serializer.data)
