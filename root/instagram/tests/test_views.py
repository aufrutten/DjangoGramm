from io import BytesIO
from pathlib import Path
from shutil import rmtree

from bs4 import BeautifulSoup as bs4

import django
from django.core.files.images import ImageFile
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_protect
from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth import login

from instagram.models import User, Post


class UserNotAuthorized(TestCase):

    def setUp(self):
        self.temp_path = Path(__file__).parent / 'temp_dir'
        settings.MEDIA_ROOT = self.temp_path

        self.client = Client(enforce_csrf_checks=True)

    def tearDown(self) -> None:
        rmtree(self.temp_path, ignore_errors=True)

    def test_root_url(self):
        response = self.client.get(reverse('root'), follow=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.redirect_chain, [('/home/', 302), ('/login/?next=/home/', 302)])

    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(
            [input.attrs.get("name") for input in parser.find_all('input')],
            ['csrfmiddlewaretoken', 'surname', 'name', 'date_of_birth', 'email', 'password', None]
        )

    def test_register_post(self):
        data = {'name': 'TestName',
                'surname': 'TestSurname',
                'date_of_birth': '2000-01-01',
                'email': 'kworil20@gmail.com',
                'password': '1234'}
        # basic register
        response = self.client.post(reverse('register'), data, follow=True)
        confirm_url = response.redirect_chain[0][0]
        parser = bs4(response.content, 'html.parser')

        # check what is in page
        self.assertEqual(parser.find('h3').text, 'Confirm Code')
        self.assertEqual(parser.find('label').text, 'kworil20@gmail.com')

        # check inputs
        inputs = [_input.attrs for _input in parser.find_all('input')]
        self.assertEqual(inputs[0]['name'], 'csrfmiddlewaretoken')

        self.assertEqual(inputs[1]['placeholder'], 'Code')
        self.assertEqual(inputs[1]['name'], 'code')
        self.assertEqual(inputs[1]['type'], 'text')

        self.assertEqual(inputs[2]['type'], 'submit')
        self.assertEqual(inputs[2]['value'], 'cancel')
        self.assertEqual(inputs[2]['name'], 'cancel')

        user = User.objects.get(email=data['email'])
        self.assertEqual(len(user.confirm_code), 10)
        self.assertIs(user.is_active, False)

        # enter wrong confirm code
        response_wrong = self.client.post(response.redirect_chain[0][0], data={'code': 'wrong_code'})
        self.assertEqual(response_wrong.status_code, 404)
        self.assertEqual(bs4(response_wrong.content, 'html.parser').find('h1').text, '404 Page Not Found')

        # press "Cancel"
        response = self.client.post(response.redirect_chain[0][0], data={'cancel': 'cancel'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain, [('/register/', 302)])
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=data['email'])

        # enter correct code
        response = self.client.post(reverse('register'), data, follow=True)
        user = User.objects.get(email=data['email'])
        confirm_code = user.confirm_code
        response = self.client.post(response.redirect_chain[0][0], data={'code': confirm_code}, follow=True)
        user = User.objects.get(email=data['email'])
        self.assertIs(user.is_active, True)
        self.assertEqual(response.redirect_chain, [('/home/', 302), ('/login/?next=/home/', 302)])

        # trying register with the same email
        response = Client().post(reverse('register'), data, follow=True)
        parser = bs4(response.content, 'html.parser')
        inputs = parser.find_all('input')
        self.assertEqual(inputs[4].attrs['placeholder'], 'Email is already exist')

        # trying access to page after confirm
        response = self.client.get(confirm_url, follow=True)
        self.assertEqual(response.redirect_chain, [('/home/', 302), ('/login/?next=/home/', 302)])

        # trying access to page while user not auth
        response = Client().get(reverse('confirm_email', args=['test@gmail.com']), follow=True)
        self.assertEqual(response.status_code, 404)


class UserAuthorized(TestCase):

    def setUp(self):
        self.temp_path = Path(__file__).parent / 'temp_dir'
        settings.MEDIA_ROOT = self.temp_path

        self.client = Client(enforce_csrf_checks=True)
        self.data = {'first_name': 'TestName',
                     'last_name': 'TestSurname',
                     'birthday': '2000-01-01',
                     'email': 'kworil20@gmail.com',
                     'username': 'kworil20@gmail.com',
                     'password': '1234',
                     'confirm_code': 'CoNfIrM_Code'}
        User.objects.create_user(**self.data)
        self.client.login(username=self.data['email'], password=self.data['password'])

    def tearDown(self) -> None:
        rmtree(self.temp_path, ignore_errors=True)

    def test_home(self):
        """without posts"""
        response = self.client.get(reverse('home'), follow=True)
        parser = bs4(response.content, 'html.parser')
        headers_buttons = [[button.attrs["href"], button.text] for button in parser.find_all('a')]
        self.assertEqual(headers_buttons, [['/home/', 'Home'],
                                           ['/profile/', 'Profile'],
                                           ['/add_post/', '+Post'],
                                           ['/logout/', 'Logout']])

    def test_redirect_to_own_profile(self):
        response = self.client.get(reverse('profile'), follow=True)
        self.assertEqual(response.redirect_chain, [('/profile/1', 302)])

    def test_get_not_exist_profile(self):
        response = self.client.get(reverse('profile', args=[1234567]))
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(parser.find('h1').text, '404 Page Not Found')

    def test_get_add_post_page(self):
        """getting page"""
        response = self.client.get(reverse('add_post'))
        parser = bs4(response.content, 'html.parser')
        _input = [[_input.attrs.get('type'), _input.attrs.get('name')] for _input in parser.find_all('input')]
        self.assertEqual(_input, [['hidden', 'csrfmiddlewaretoken'],
                                  ['file', 'photo'],
                                  [None, 'tags'],
                                  ['submit', None]])

    def test_post_add_post_page(self):
        img_path = Path(__file__).parent / 'img' / 'test_image.png'
        client = Client(enforce_csrf_checks=True)
        client.login(username=self.data['username'], password=self.data['password'])
        with open(img_path, 'rb') as img:
            response = client.post(reverse('add_post'), {'tags': '#1488', 'photo': img}, follow=True)
        self.assertEqual(response.redirect_chain, [('/profile/1', 302)])
        parser = bs4(response.content, 'html.parser')
        path = parser.find('img').attrs.get('src')
        path = path[:30] + path[-4:]
        '/media/users/images/test_image_YEusAN9.png'
        self.assertEqual(path, '/media/users/images/test_image.png')

    def test_home_like(self):
        img_path = Path(__file__).parent / 'img' / 'test_image.png'

        with img_path.open(mode='rb') as img:
            self.client.post(reverse('add_post'), {'tags': '#1488', 'photo': img}, follow=True)

        response = self.client.get(reverse('home'))
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(parser.find('button').text, 'Likes: 0')

        response = self.client.post(reverse('home'), {'like': 1}, follow=True)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(parser.find('button').text, 'Likes: 1')

    def test_profile_like(self):
        img_path = Path(__file__).parent / 'img' / 'test_image.png'
        with img_path.open(mode='rb') as img:
            self.client.post(reverse('add_post'), {'tags': '#1488', 'photo': img}, follow=True)

        response = self.client.get(reverse('profile', args=[1]), follow=True)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(parser.find('button').text, 'Likes: 0')

        response = self.client.post(reverse('profile', args=[1]), {'like': '1'}, follow=True)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(parser.find('button').text, 'Likes: 1')

        response = self.client.post(reverse('profile', args=[1]), {'like': '1'}, follow=True)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(parser.find('button').text, 'Likes: 0')

    def test_comment_page(self):
        img_path = Path(__file__).parent / 'img' / 'test_image.png'
        with img_path.open(mode='rb') as img:
            self.client.post(reverse('add_post'), {'tags': '#1488', 'photo': img}, follow=True)

        response = self.client.get(reverse('comments', args=[1]), follow=True)
        parser = bs4(response.content, 'html.parser')
        _inputs = [[_input.attrs.get('name'), _input.attrs.get('type')] for _input in parser.findAll('input')]
        self.assertEqual(_inputs, [['csrfmiddlewaretoken', 'hidden'], ['comment', 'text'], [None, 'submit']])

    def test_comment_wrong_page(self):
        response = self.client.get(reverse('comments', args=[99999999999999]), follow=True)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(parser.find('h1').text, '404 Page Not Found')

    def test_comment_post(self):
        img_path = Path(__file__).parent / 'img' / 'test_image.png'
        with img_path.open(mode='rb') as img:
            self.client.post(reverse('add_post'), {'tags': '#1488', 'photo': img}, follow=True)
        data = {'comment': 'TestComment'}
        response = self.client.post(reverse('comments', args=[1]), follow=True, data=data)
        parser = bs4(response.content, 'html.parser')
        comment = parser.find_all('label')[1].text
        self.assertEqual(comment, data['comment'])


class TestLogin(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 401)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(
            [input.attrs.get("name") for input in parser.find_all('input')],
            ['csrfmiddlewaretoken', 'email', 'password', None, None, None]
        )

    def test_login_wrong_email(self):
        data = {'email': 'email_not@exist.com', 'password': '1234'}
        response = self.client.post(reverse('login'), data=data)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual([input for input in parser.find_all('input')][1].attrs['placeholder'],
                         "That email isn't exists")

    def test_login_wrong_password(self):
        data = {'email': 'test@test.com', 'password': '1234'}

        User.objects.create_user(username=data['email'], email=data['email'], password='other_pass',
                                 birthday='2000-01-01')

        response = self.client.post(reverse('login'), data=data)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual([input for input in parser.find_all('input')][2].attrs['placeholder'],
                         "password isn't correct")

    def test_login_correct(self):
        data = {'email': 'test@test.com', 'password': '1234'}

        User.objects.create_user(username=data['email'], email=data['email'], password='1234',
                                 birthday='2000-01-01')

        response = self.client.post(reverse('login'), data=data, follow=True)
        self.assertEqual(response.redirect_chain, [('/home/', 302)])

    def test_login_if_user_is_not_active(self):
        data = {'email': 'test@test.com', 'password': '1234'}

        User.objects.create_user(username=data['email'], email=data['email'], password='1234',
                                 birthday='2000-01-01', is_active=False)
        response = self.client.post(reverse('login'), data=data, follow=True)
        parser = bs4(response.content, 'html.parser')
        self.assertEqual(parser.find('h3').text, 'Confirm Code')
        self.assertEqual(parser.find('label').text, data['email'])

    def test_logout(self):
        data = {'email': 'test@test.com', 'password': '1234'}

        User.objects.create_user(username=data['email'], email=data['email'], password=data['password'],
                                 birthday='2000-01-01')

        response = self.client.post(reverse('login'), data=data, follow=True)
        self.assertEqual(response.redirect_chain, [('/home/', 302)])
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.redirect_chain, [('/login/', 302)])
