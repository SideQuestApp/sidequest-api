from django.db import models
from django.contrib.postgres.fields import ArrayField
from common.models import AbstractBaseModel

status = (("NS" , "Not Started"), ("IP" , "In Progress"), ("F" , "Finished"), ("IC" , "Incomplete"))


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
    first_node = models.ForeignKey(QuestNode, on_delete=models.CASCADE, related_name='first_node', blank=True, null=True)
    last_node = models.ForeignKey(QuestNode, on_delete=models.CASCADE, related_name='last_node', blank=True, null=True)
    price_low = models.IntegerField()
    price_high = models.IntegerField()

    def __str__(self):
        return self.name
