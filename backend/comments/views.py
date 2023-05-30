from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import verify_recaptcha
from .models import Comment
from .serializers import CommentSerializer


class CommentPagination(PageNumberPagination):
    page_size = 25


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

    def create(self, request, *args, **kwargs):
        captcha_token = self.request.data.get('captcha')
        is_captcha_valid = verify_recaptcha(captcha_token)

        if not is_captcha_valid:
            return Response({'error': 'Invalid reCAPTCHA token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CommentRepliesAPIView(APIView):
    def get(self, request, parent_id):
        parent_comment = Comment.objects.get(id=parent_id)
        replies = parent_comment.replies.all()
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)
