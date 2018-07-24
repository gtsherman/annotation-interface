from django.contrib.auth.models import User
from django.db import models


class Document(models.Model):
    docno = models.CharField(max_length=50)
    text = models.TextField()
    index = models.CharField(max_length=100)

    def __str__(self):
        return self.docno


class DocumentAssignment(models.Model):
    INCOMPLETE = 0
    SKIPPED = 1
    COMPLETE = 2

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skippable = models.BooleanField(default=True)
    complete = models.SmallIntegerField(default=INCOMPLETE)


class Term(models.Model):
    term = models.CharField(max_length=200)

    def __str__(self):
        return self.term

    class Meta:
        ordering = ['term']


class QualityCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, null=True, on_delete=models.PROTECT)
    checked = models.BooleanField(default=False)


class DocumentTerm(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)


class TopicTerms(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    document = models.ForeignKey(Document, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, on_delete=models.PROTECT)

    def __str__(self):
        return '<{}, {}: {}>'.format(str(self.user), str(self.document), str(self.term))
