import random

from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Model
from django.shortcuts import get_object_or_404, reverse, HttpResponseRedirect
from django.views import generic

from .models import Document, Term, DocumentTerm, TopicTerms, QualityCheck, DocumentAssignment


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'topicterms/home.html'

    def get_queryset(self):
        return DocumentAssignment.objects.filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['complete_docs'] = DocumentAssignment.objects.filter(user=self.request.user,
                                                                     complete=DocumentAssignment.COMPLETE)
        context['incomplete_docs'] = DocumentAssignment.objects.filter(user=self.request.user,
                                                                       complete=DocumentAssignment.INCOMPLETE).order_by(
            'skippable')
        context['skipped_docs'] = DocumentAssignment.objects.filter(user=self.request.user,
                                                                    complete=DocumentAssignment.SKIPPED)

        return context


class AnnotateView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    template_name = 'topicterms/annotate.html'
    model = Document

    def get_object(self):
        document = super().get_object()

        # Will need to parse out any potentially problematic parts of the HTML, and may need to inject a quality check
        doc_html = BeautifulSoup(document.text, 'html.parser')

        # Remove <head> and definitely any <base> elements
        try:
            doc_html.head.extract()
        except AttributeError:
            pass
        try:
            doc_html.base.extract()
        except AttributeError:
            pass

        # randomly include some specific instructions as a quality check for the user input
        if QualityCheck.objects.filter(user=self.request.user, document=document).exists():
            term = QualityCheck.objects.get(user=self.request.user, document=document).term
        elif random.randint(0, 4) == 0:
            term = Term.objects.order_by('?').first()
        else:
            term = None

        QualityCheck.objects.get_or_create(user=self.request.user, document=document, term=term)

        if term is not None:
            please_select = doc_html.new_tag('p')
            please_select.string = 'Please select the following term: {}'.format(term.term)

            try:
                doc_html.p.insert_after(please_select)
            except AttributeError: # no <p> in the document for some reason
                doc_html.append(please_select)

            document.quality_check_term = term

        document.text = str(doc_html)
        return document

    def test_func(self):
        return DocumentAssignment.objects.filter(document=self.kwargs['pk'], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        document = self.object
        quality_check_active = hasattr(document, 'quality_check_term')

        context['document_assignment'] = DocumentAssignment.objects.get(document=document, user=self.request.user)
        context['terms'] = [document_term.term for document_term in DocumentTerm.objects.filter(
            document=document).order_by('term')]
        if quality_check_active:
            context['terms'].append(document.quality_check_term)
            context['terms'] = sorted(context['terms'], key=lambda t: t.term)
        context['topic_terms'] = [topic_term.term for topic_term in TopicTerms.objects.filter(user=self.request.user,
                                                                                              document=document)]
        context['limit'] = 11 if quality_check_active else 10

        return context


@login_required
def record_annotation(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    try:
        document_assignment = DocumentAssignment.objects.get(document=document, user=request.user)
    except Model.DoesNotExist:
        messages.error(request, 'You do not appear to have been assigned this document.')
        return HttpResponseRedirect(reverse('topicterms:index'))

    if not request.POST.getlist('terms'):
        messages.error(request, 'You must provide at least one term. If you cannot select a term, please use the skip '
                                'button.')
        return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))

    limit = 10
    quality_check = QualityCheck.objects.get(user=request.user, document=document)
    if quality_check.term is not None:
        limit += 1

    if len(request.POST.getlist('terms')) > limit:
        messages.error(request, 'You may only select up to {} terms. Please select fewer terms.'.format(str(limit)))
        return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))

    # Clear existing annotations to make room for the new ones
    TopicTerms.objects.filter(user=request.user, document=document).delete()

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

    document_assignment.complete = DocumentAssignment.COMPLETE
    document_assignment.save()

    try:
        next_doc = DocumentAssignment.objects.filter(user=request.user, complete=DocumentAssignment.INCOMPLETE).order_by(
            'skippable')[0].document
    except IndexError:
        return HttpResponseRedirect(reverse('topicterms:index'))

    return HttpResponseRedirect(reverse('topicterms:annotate', args=(next_doc.pk,)))


@login_required
def skip_annotation(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    try:
        document_assignment = DocumentAssignment.objects.get(document=document, user=request.user)

        if document_assignment.skippable and document_assignment.complete == DocumentAssignment.INCOMPLETE:
            document_assignment.complete = DocumentAssignment.SKIPPED
            document_assignment.save()
        else:
            messages.info(request, 'This document may not be skipped.')
            return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))
    except Model.DoesNotExist:
        messages.error(request, 'You do not appear to be assigned this document.')
        return HttpResponseRedirect(reverse('topicterms:index'))

    try:
        next_doc = DocumentAssignment.objects.filter(user=request.user, complete=DocumentAssignment.INCOMPLETE).order_by(
            'skippable')[0].document
    except IndexError:
        return HttpResponseRedirect(reverse('topicterms:index'))

    return HttpResponseRedirect(reverse('topicterms:annotate', args=(next_doc.pk,)))
