from django.db import models
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

    def __str__(self):
        return self.name


class QuestMap(AbstractBaseModel):
    name = models.CharField(max_length=80)

    def __str__(self) -> str:
        return self.name


class QuestTree(AbstractBaseModel):
    """
    * Quest Tree Model...
    """
    name = models.CharField(max_length=80)
    description = models.CharField(max_length=10000)
    status = models.CharField(max_length=20, choices=status)
    completion_exp = models.IntegerField()
    first_node = models.ForeignKey(QuestNode, on_delete=models.CASCADE, related_name='first_node')
    last_node = models.ForeignKey(QuestNode, on_delete=models.CASCADE, related_name='last_node')
    price_low = models.IntegerField()
    price_high = models.IntegerField()
    relations = models.ForeignKey(QuestMap, on_delete=models.CASCADE, related_name='relation_map')

    def __str__(self):
        return self.name


class NodeRelation(AbstractBaseModel):
    """
    * Node Relations model.
    * This model allows for node relations
    """
    first = models.ForeignKey(QuestNode, on_delete=models.CASCADE, related_name='first_relation')
    second = models.ForeignKey(QuestNode, on_delete=models.CASCADE, related_name='second_relation')
    relations_map = models.ForeignKey(QuestMap, on_delete=models.CASCADE, related_name='relations_map')

    def __str__(self):
        return f'{self.first} - {self.second}'
