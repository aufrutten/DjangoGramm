
import django
from django.test import TestCase

from instagram import models
from instagram import views


class TestModels(TestCase):

    def test_post(self):
        """models.Post; models.Tag; models.Comment; models.Like"""
        img_url = 'https://i.imgur.com/Uzr9fRm.png'
        user = models.User.objects.create_user(first_name='Name',
                                               last_name='Surname',
                                               username='UsernameTest',
                                               password='1234',
                                               birthday='2000-01-01')
        tag = models.Tag(tag='#Love')
        tag.save()
        post = models.Post(user=user, image=img_url)
        post.save()
        post.tags.add(tag)
        text_post = post.__str__()
        text_tag = tag.__str__()

        self.assertEqual(text_post, 'post:1 user:1, tags:#Love')
        self.assertEqual(text_tag, '#Love')

        comment = models.Comment(user=user, post=post, comment='TestComment')
        comment.save()
        text_comment = comment.__str__()

        self.assertEqual(text_comment, 'comment:1 [user:1 post:1]')
        self.assertEqual(comment.comment, 'TestComment')

        like = models.Like(user=user, post=post)
        like.save()
        text_like = like.__str__()

        self.assertEqual(text_like, 'user:1 post:1')

        with self.assertRaises(django.db.utils.IntegrityError):
            like = models.Like(user=user, post=post)
            like.save()

    def test_generate_code_confirm(self):
        confirm_code = views.generate_code()
        self.assertEqual(len(confirm_code), 10)

