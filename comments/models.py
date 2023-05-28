import os
import uuid

from django.utils.text import slugify
from django.db import models


def create_custom_path_image(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user_name)}-{uuid.uuid4()}{extension}"
    return os.path.join("images/", filename)


def create_custom_path_file(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user_name)}-{uuid.uuid4()}{extension}"
    return os.path.join("files/", filename)


class Comment(models.Model):
    user_name = models.CharField(max_length=255)
    email = models.EmailField()
    home_page = models.URLField(blank=True)
    captcha = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(null=True, upload_to=create_custom_path_file)
    image = models.ImageField(null=True, upload_to=create_custom_path_image)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return self.text[:50]

    class Meta:
        ordering = ['-created_at']
