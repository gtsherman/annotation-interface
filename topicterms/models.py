from django.contrib.auth.models import User
from django.db import models


class Document(models.Model):
    docno = models.CharField(max_length=50)
    text = models.TextField()
    annotator = models.ManyToManyField(User)

    def __str__(self):
        return self.docno


class Term(models.Model):
    term = models.CharField(max_length=200)
    documents = models.ManyToManyField(Document)

    def __str__(self):
        return self.term


class TopicTerms(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, on_delete=models.PROTECT)

    def __str__(self):
        return '<{}, {}: {}>'.format(str(self.user), str(self.document), str(self.term))
