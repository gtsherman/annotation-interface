import random

from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, reverse, HttpResponseRedirect
from django.views import generic

from .models import Document, Term, DocumentTerm, TopicTerms, QualityCheck


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'topicterms/home.html'

    def get_queryset(self):
        return Document.objects.filter(annotator=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['complete_docs'] = Document.objects.filter(annotator=self.request.user, complete=Document.COMPLETE)
        context['incomplete_docs'] = Document.objects.filter(annotator=self.request.user,
                                                             complete=Document.INCOMPLETE).order_by('skippable')
        context['skipped_docs'] = Document.objects.filter(annotator=self.request.user, complete=Document.SKIPPED)
        return context


class AnnotateView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    template_name = 'topicterms/annotate.html'
    model = Document

    def get_object(self):
        document = super().get_object()

        # randomly include some specific instructions as a quality check for the user input
        if QualityCheck.objects.filter(user=self.request.user, document=document).exists():
            term = QualityCheck.objects.get(user=self.request.user, document=document).term
        elif random.randint(0, 4) == 0:
            term = Term.objects.order_by('?').first()
        else:
            term = None

        QualityCheck.objects.get_or_create(user=self.request.user, document=document, term=term)

        if term is not None:
            doc_html = BeautifulSoup(document.text, 'html.parser')

            please_select = doc_html.new_tag('p')
            please_select.string = 'Please select the following term: {}'.format(term.term)

            doc_html.p.insert_after(please_select)

            document.text = str(doc_html)
            document.quality_check_term = term

        return document

    def test_func(self):
        return Document.objects.filter(pk=self.kwargs['pk'], annotator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        document = self.object
        quality_check_active = hasattr(document, 'quality_check_term')

        context['terms'] = [document_term.term for document_term in DocumentTerm.objects.filter(
            document=document).order_by('term')]
        if quality_check_active:
            context['terms'].append(document.quality_check_term)
            context['terms'] = sorted(context['terms'], key=lambda t: t.term)
        context['topic_terms'] = [topic_term.term for topic_term in TopicTerms.objects.filter(user=self.request.user,
                                                                                              document=document)]
        context['next_doc'] = Document.objects.filter(annotator=self.request.user, complete=Document.INCOMPLETE)[0]
        context['limit'] = 11 if quality_check_active else 10

        return context


@login_required
def record_annotation(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.user not in document.annotator.all():
        messages.error(request, 'You do not appear to have been assigned this document.')
        return HttpResponseRedirect(reverse('topicterms:index'))

    # Clear existing annotations to make room for the new ones
    TopicTerms.objects.filter(user=request.user, document=document).delete()

    if not request.POST.getlist('terms'):
        messages.error(request, 'You must provide at least one term. If you cannot select a term, please use the skip'
                                'button.')
        return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))

    limit = 10
    quality_check = QualityCheck.objects.get(user=request.user, document=document)
    if quality_check.term is not None:
        limit += 1

    if len(request.POST.getlist('terms')) > limit:
        messages.error(request, 'You may only select up to {} terms. Please select fewer terms.'.format(str(limit)))
        return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))

    try:
        for term_id in request.POST.getlist('terms'):
            term = get_object_or_404(Term, pk=term_id)
            if term == quality_check.term:
                quality_check.checked = True
                quality_check.save()
            else:  # just a standard TopicTerm
                if term in [document_term.term for document_term in DocumentTerm.objects.filter(document=document)]:
                    topic_term = TopicTerms(user=request.user, document=document, term=term)
                    topic_term.save()
                else:
                    messages.error(request, 'This term does not appear to have been an option: {}'.format(term.term))
                    return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))
    except KeyError:
        return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))

    document.complete = Document.COMPLETE
    document.save()

    next_doc = Document.objects.filter(annotator=request.user, complete=Document.INCOMPLETE)[0]
    if next_doc is None:
        return HttpResponseRedirect(reverse('topicterms:index'))

    return HttpResponseRedirect(reverse('topicterms:annotate', args=(next_doc.pk,)))


@login_required
def skip_annotation(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.user in document.annotator.all():
        if document.skippable and document.complete == Document.INCOMPLETE:
            document.complete = Document.SKIPPED
            document.save()
        else:
            messages.info(request, 'This document may not be skipped.')
            return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))

    next_doc = Document.objects.filter(annotator=request.user, complete=Document.INCOMPLETE)[0]
    if next_doc is None:
        return HttpResponseRedirect(reverse('topicterms:index'))

    return HttpResponseRedirect(reverse('topicterms:annotate', args=(next_doc.pk,)))
