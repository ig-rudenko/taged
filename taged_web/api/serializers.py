from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from taged_web.models import Tags, User


class NoteSerializerNoTagsValidation(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=True)
    tags = serializers.ListSerializer(child=serializers.CharField(), required=True)
    content = serializers.CharField(required=True)


class NoteSerializerTagsValidation(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=True)
    tags = serializers.ListSerializer(child=serializers.CharField(), required=True)
    content = serializers.CharField(required=True)

    def validate_tags(self, values):
        if Tags.objects.filter(tag_name__in=values).count() == len(values):
            return values
        raise ValidationError("Некоторые указанные вами теги не существуют")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "is_staff", "is_superuser")
