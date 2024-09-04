from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Tag(models.Model):
    label = models.CharField(max_length=255)


class TaggedItemManageer(models.Model):
    def get_tags_for(self, object_id, object_type):
        content_type = ContentType.objects.get_for_model(object_type)
        queryset = TaggedItem.objects \
        .select_related('tag') \
        .filter(
            content_type = content_type,
            obj_id = object_id
        )
        return queryset



class TaggedItem(models.Model):
    objects = TaggedItemManageer()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
