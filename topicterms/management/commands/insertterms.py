from collections import defaultdict

from django.core.management.base import BaseCommand

from topicterms.models import Document, DocumentTerm, Term


class Command(BaseCommand):
    help = 'Inserts term data from the specified location'

    def add_arguments(self, parser):
        parser.add_argument('data_location', nargs='+')

    def handle(self, *args, **options):
        termdocs = defaultdict(list)

        data_files = options['data_location']
        for data_file in data_files:
            with open(data_file) as f:
                for line in f:
                    terms = line.strip().split(',')
                    docno = terms.pop(0)

                    for term in terms:
                        termdocs[term].append(docno)

        terms = [Term(term=term) for term in termdocs]
        term_chunks = self._chunks(terms, 999)
        for chunk in term_chunks:
            Term.objects.bulk_create(chunk)

        documentterms = [
            DocumentTerm(term=Term.objects.get(term=term), document=Document.objects.get(docno=docno)) for term in
            termdocs for docno in termdocs[term] if Document.objects.filter(docno=docno).exists()
        ]

        documentterm_chunks = self._chunks(documentterms, 999)
        for chunk in documentterm_chunks:
            DocumentTerm.objects.bulk_create(chunk)

    def _chunks(self, data, n):
        chunks = []
        for i in range(0, len(data), n):
            chunks.append(data[i:i+n])
        return chunks
