from django.core.management import BaseCommand

from topicterms.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        TopicTerms.objects.all().delete()
        DocumentTerm.objects.all().delete()
        Document.objects.all().delete()
        Term.objects.all().delete()
