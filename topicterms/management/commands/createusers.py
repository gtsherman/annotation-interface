import json
import random
import string

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from topicterms.models import Document


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('num_users')

    def handle(self, *args, **options):
        usernames = [''.join(random.choice(string.ascii_uppercase) for _ in range(5)) for _ in range(int(
                                                                                                options['num_users']))]
        passwords = [''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
                     for _ in range(len(usernames))]
        users = [User.objects.create_user(usernames[i], password=passwords[i]) for i in range(len(usernames))]

        irr_docs = Document.objects.all().order_by('?')[:10]
        for doc in irr_docs:
            doc.annotator.add(*users)
            doc.skippable = False
            doc.save()

        for user in users:
            assigned_docs = Document.objects.exclude(id__in=[doc.id for doc in irr_docs])[:300]
            user.document_set.add(*assigned_docs)

        print('Created the following users:')
        for i in range(len(users)):
            print(usernames[i], passwords[i], sep=', ')
