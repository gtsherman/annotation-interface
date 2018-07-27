import json
import random
import string

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from topicterms.models import Document, DocumentAssignment


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('num_users', type=int, help='The number of users to create.')
        parser.add_argument('-s', '--shared', type=int, default=15, help='The number of documents shared among '
                                                                          'users. These are documents that will be '
                                                                          'unskippable and assigned to all users to '
                                                                          'enable inter-rater reliability metrics. '
                                                                          'Default is 15.')
        parser.add_argument('-d', '--docs', type=int, default=300, help='The number of documents assigned to '
                                                                               'each user in addition to any shared '
                                                                               'documents. These documents may be '
                                                                               'assigned to more than one user, '
                                                                               'but will not include any of the '
                                                                               'shared documents. Default is 300.')

    def handle(self, *args, **options):
        usernames = [''.join(random.choice(string.ascii_uppercase) for _ in range(5)) for _ in range(options[
                                                                                                         'num_users'])]
        passwords = [''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
                     for _ in range(len(usernames))]
        users = [User.objects.create_user(usernames[i], password=passwords[i]) for i in range(len(usernames))]

        irr_docs = Document.objects.all().order_by('?')[:options['shared']]
        DocumentAssignment.objects.bulk_create([DocumentAssignment(user=user, document=document, skippable=False) for
                                                user in users for document in irr_docs])

        for user in users:
            assigned_docs = Document.objects.exclude(id__in=[doc.id for doc in irr_docs]).order_by('?')[:options[
                'docs']]
            DocumentAssignment.objects.bulk_create([DocumentAssignment(user=user, document=doc) for doc in assigned_docs])

        print('Created the following users:')
        for i in range(len(users)):
            print(usernames[i], passwords[i], sep=', ')
