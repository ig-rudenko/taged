from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ListSerializer, CharField, Serializer, ModelSerializer, IntegerField

from taged_web.models import Tags, User


class NoteSerializerNoTagsValidation(Serializer):
    title = CharField(max_length=255, required=True)
    tags: ListSerializer[CharField] = ListSerializer(child=CharField(), required=True)
    content = CharField(required=True)


class NoteSerializerTagsValidation(Serializer):
    title = CharField(max_length=255, required=True)
    tags: ListSerializer[CharField] = ListSerializer(child=CharField(), required=True)
    content = CharField(required=True)

    def validate_tags(self, values):
        if Tags.objects.filter(tag_name__in=values).count() == len(values):
            return values
        raise ValidationError("Некоторые указанные вами теги не существуют")


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser")


class CreateTempLinkSerializer(Serializer):
    minutes = IntegerField(required=True, min_value=1, max_value=60 * 24)
