from django.db import models
from django.contrib.postgres.fields import ArrayField
from common.models import AbstractBaseModel
from django.core.validators import MaxValueValidator, MinValueValidator

status = (("NS" , "Not Started"), ("IP" , "In Progress"), ("F" , "Finished"), ("IC" , "Incomplete"))
langchain_models = (("gpt-4", "gpt-4"), ("gpt-4-turbo", "gpt-4-turbo"), ("claude-3-sonnet-20240229", "claude-3"), ("gemini-pro", "gemini-pro"))


class LangChainVars(AbstractBaseModel):
    """
    * This model is used to configure LangChain prompting
    * It stores the model used, system prompt, max tokens for response and etc
    """
    model = models.CharField(max_length=100, choices=langchain_models)
    max_tokens = models.IntegerField(default=2000)
    system_prompt = models.TextField(max_length=300000)
    rag_docu_url = models.URLField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.model


class QuestNode(AbstractBaseModel):
    """
    * Quest Node Model
    """
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=2000)
    longitude = models.FloatField()
    latitude = models.FloatField()
    status = models.CharField(max_length=20, choices=status)
    price_low = models.IntegerField()
    price_high = models.IntegerField()
    optional = models.BooleanField(default=False)
    completion_experience = models.IntegerField()
    next = models.ManyToManyField("QuestNode", blank=True)
    quest = models.ForeignKey("QuestTree", on_delete=models.CASCADE, related_name='quest_tree', blank=True)
    # Chain is the foreign key for which LangChain configuration was used to create this
    chain = models.ForeignKey(LangChainVars, on_delete=models.CASCADE, related_name='node_langchain_config', blank=True, null=True)

    def __str__(self):
        return self.name


class QuestTree(AbstractBaseModel):
    """
    * Quest Tree Model...
    """
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=10000)
    status = models.CharField(max_length=20, choices=status)
    completion_exp = models.IntegerField()
    location = models.CharField(max_length=200, default='East Lansing, MI, USA')
    first_node = models.ForeignKey(QuestNode, on_delete=models.CASCADE, related_name='first_node', blank=True, null=True)
    last_node = models.ForeignKey(QuestNode, on_delete=models.CASCADE, related_name='last_node', blank=True, null=True)
    price_low = models.IntegerField()
    price_high = models.IntegerField()
    # Chain is the foreign key for which LangChain configuration was used to create this
    chain = models.ForeignKey(LangChainVars, on_delete=models.CASCADE, related_name='tree_langchain_config', blank=True, null=True)

    def __str__(self):
        return self.name


class QuestReviews(AbstractBaseModel):
    """
    * Quest Reviews. This table is mostly used to gauge performance in general and also
    * for our langchain configurations.
    """

    quest = models.ForeignKey(QuestTree, on_delete=models.CASCADE, related_name='quest_reviewed')
    chain = models.ForeignKey(LangChainVars, on_delete=models.CASCADE, related_name='langchain_config')
    user = models.ForeignKey("profiles.User", on_delete=models.CASCADE, related_name='user_reviewing')
    score = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f'{self.user}-{self.quest}-{self.score}'
