from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json

# Create your tests here.

client = Client()

class NewPostCreate(TestCase):

    def setUp(self):
        self.payload = {
            "post-content":"aaa"
        }

    def test_new_post(self):
        response = client.post(
            reverse('create'), 
            self.payload,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
