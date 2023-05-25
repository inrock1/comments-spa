from rest_framework import serializers
from .models import Comment


# class AttachmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Attachment
#         fields = ('id', 'file', 'file_type')



class CommentSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    # attachments = AttachmentSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'user_name', 'email', 'home_page', 'captcha', 'text', 'created_at', 'parent', 'replies', 'image', "file")

    def get_replies(self, obj):
        serializer = self.__class__(obj.replies.all(), many=True)
        serializer.bind('', self)
        return serializer.data

