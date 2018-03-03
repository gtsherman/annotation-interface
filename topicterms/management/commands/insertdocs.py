import json

from django.core.management.base import BaseCommand

from topicterms.models import Document


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('data_location')

    def handle(self, *args, **options):
        with open(options['data_location'], encoding='latin-1') as f:
            docs = json.load(f)

            chunks = self._chunks([Document(docno=doc, text=docs[doc]['text'], index=docs[doc]['index']) for doc in
                                   docs], 999)
            for chunk in chunks:
                Document.objects.bulk_create(chunk)

    def _chunks(self, data, n):
        chunks = []
        for i in range(0, len(data), n):
            chunks.append(data[i:i+n])
        return chunks
