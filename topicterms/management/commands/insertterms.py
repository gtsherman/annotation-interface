from collections import defaultdict

from django.core.management.base import BaseCommand

from topicterms.models import Document, DocumentTerm, Term


class Command(BaseCommand):
    help = 'Inserts term data from the specified location'

    def add_arguments(self, parser):
        parser.add_argument('data_location')

    def handle(self, *args, **options):
        termdocs = defaultdict(list)
        with open(options['data_location']) as f:
            for line in f:
                terms = line.strip().split(',')
                docno = terms.pop(0)

                for term in terms:
                    termdocs[term].append(docno)

        for term in termdocs:
            term = Term(term=term)
            term.save()

            for doc in termdocs[term]:
                doc = Document.objects.get(docno=doc)
                DocumentTerm(term=term, doc=doc).save()
