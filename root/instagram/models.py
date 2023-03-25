from django.contrib.auth.models import User as UserDjango
from django.conf import settings
from django.db import models

from cloudinary.models import CloudinaryField


class User(UserDjango):

    birthday = models.DateField(null=False)
    confirm_code = models.CharField(null=False, max_length=10)

    def __str__(self):
        return self.username

    def __int__(self):
        return self.id


class Subscription(models.Model):

    from_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='to_user')

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f'from {self.from_user} to {self.to_user}'


class Post(models.Model):

    id = models.BigAutoField(primary_key=True, auto_created=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    tags = models.ManyToManyField("Tag", blank=True)

    def __str__(self):
        tags = ', '.join([str(tag) for tag in self.tags.all()])
        return f'post:{self.id} user:{self.user.id}, tags:{tags}'

    def __int__(self):
        return self.id


class Tag(models.Model):

    id = models.BigAutoField(primary_key=True, auto_created=True)
    tag = models.CharField(null=False, unique=True, max_length=20)

    def __str__(self):
        return f"{self.tag}"


class Comment(models.Model):

    id = models.BigAutoField(primary_key=True, auto_created=True)
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    comment = models.TextField(max_length=300)

    def __str__(self):
        return f'comment:{self.id} [user:{self.user.id} post:{self.post.id}]'

    def __int__(self):
        return self.id


class Like(models.Model):

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'post']

    def __str__(self):
        return f'{self.user} post:{self.post.id}'

    def __int__(self):
        return self.id


class Image(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    image = CloudinaryField("Image") if settings.DEBUG is False else models.ImageField(null=False,
                                                                                       blank=True,
                                                                                       upload_to='users/images')
