from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment
from .serializers import CommentSerializer


class CommentPagination(PageNumberPagination):
    page_size = 3


class CommentAPIView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        parent_id = self.request.query_params.get('parent_id')
        queryset = Comment.objects.filter(parent__isnull=True)
        if parent_id:
            queryset = Comment.objects.filter(parent_id=parent_id)
        return queryset


class CommentRepliesAPIView(APIView):
    def get(self, request, parent_id):
        parent_comment = Comment.objects.get(id=parent_id)
        replies = parent_comment.replies.all()
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)
