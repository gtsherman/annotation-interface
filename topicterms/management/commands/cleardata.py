from django.core.management import BaseCommand

from topicterms.models import *


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-u', '--users', action='store_true', help='Delete user accounts')

    def handle(self, *args, **options):
        QualityCheck.objects.all().delete()
        TopicTerms.objects.all().delete()
        DocumentTerm.objects.all().delete()
        Document.objects.all().delete()
        Term.objects.all().delete()
        DocumentAssignment.objects.all().delete()

        if options['users']:
            User.objects.all().delete()
