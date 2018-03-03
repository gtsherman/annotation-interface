from django.core.management import BaseCommand

from topicterms.models import TopicTerms


class Command(BaseCommand):
    help = 'Dumps the topic terms recorded by users'

    def add_arguments(self, parser):
        parser.add_argument('out_file')

    def handle(self, *args, **options):
        with open(options['out_file'], 'w') as out:
            for tt in TopicTerms.objects.all():
                print(','.join((tt.user.username, tt.document.docno, tt.document.index, tt.term.term)), file=out)
