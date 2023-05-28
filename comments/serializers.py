from rest_framework import serializers
from .models import Comment
from bleach import clean
from django.utils.safestring import mark_safe


class CommentSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    replies = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False)

    class Meta:
        model = Comment
        fields = ('id', 'user_name', 'email', 'home_page', 'captcha', 'text', 'created_at', 'parent', 'replies', 'image', "file")

    def get_replies(self, obj):
        serializer = self.__class__(obj.replies.all(), many=True)
        serializer.bind('', self)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['text'] = self.clean_html(representation['text'])
        return representation

    def clean_html(self, value):
        allowed_tags = ['a', 'code', 'i', 'strong']
        allowed_attributes = {'a': ['href', 'title']}
        cleaned_value = clean(value, tags=allowed_tags, attributes=allowed_attributes)
        return mark_safe(cleaned_value)
