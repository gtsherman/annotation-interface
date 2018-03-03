from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, reverse, HttpResponseRedirect
from django.views import generic

from .models import Document, Term, DocumentTerm, TopicTerms


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'topicterms/home.html'

    def get_queryset(self):
        return Document.objects.filter(annotator=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['complete_docs'] = Document.objects.filter(annotator=self.request.user, complete=Document.COMPLETE)
        context['incomplete_docs'] = Document.objects.filter(annotator=self.request.user, complete=Document.INCOMPLETE)
        context['skipped_docs'] = Document.objects.filter(annotator=self.request.user, complete=Document.SKIPPED)
        return context


class AnnotateView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    template_name = 'topicterms/annotate.html'
    model = Document

    def test_func(self):
        return Document.objects.filter(pk=self.kwargs['pk'], annotator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        context['terms'] = [document_term.term for document_term in DocumentTerm.objects.filter(
            document=document).order_by('term')]
        context['topic_terms'] = [topic_term.term for topic_term in TopicTerms.objects.filter(user=self.request.user,
                                                                                   document=document)]
        context['next_doc'] = Document.objects.filter(annotator=self.request.user, complete=Document.INCOMPLETE)[0]
        return context


@login_required
def record_annotation(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    # Clear existing annotations to make room for the new ones
    TopicTerms.objects.filter(user=request.user, document=document).delete()

    if not request.POST.getlist('terms'):
        messages.error(request, 'You must provide at least one term. If you cannot select a term, please use the skip button.')
        return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))

    if len(request.POST.getlist('terms')) > 10:
        messages.error(request, 'You may only select up to 10 terms. Please select fewer terms.')
        return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.pk,)))

    try:
        for term_id in request.POST.getlist('terms'):
            term = get_object_or_404(Term, pk=term_id)
            topic_term = TopicTerms(user=request.user, document=document, term=term)
            topic_term.save()
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
        if document.complete == Document.INCOMPLETE:
            document.complete = Document.SKIPPED
            document.save()

    next_doc = Document.objects.filter(annotator=request.user, complete=Document.INCOMPLETE)[0]
    if next_doc is None:
        return HttpResponseRedirect(reverse('topicterms:index'))

    return HttpResponseRedirect(reverse('topicterms:annotate', args=(next_doc.pk,)))
