from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, reverse, HttpResponseRedirect
from django.views import generic

from .models import Document, Term, TopicTerms


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'topicterms/home.html'

    def get_queryset(self):
        return Document.objects.filter(annotator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed'] = [topic_term.document for topic_term in TopicTerms.objects.filter(user=self.request.user)]
        return context


class AnnotateView(UserPassesTestMixin, generic.DetailView):
    template_name = 'topicterms/annotate.html'
    model = Document

    def test_func(self):
        return Document.objects.filter(pk=self.kwargs['pk'], annotator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        document = get_object_or_404(Document, pk=self.kwargs['pk'])
        context['topic_terms'] = [topic_term.term for topic_term in TopicTerms.objects.filter(user=self.request.user,
                                                                                   document=document)]
        return context


@login_required
def record_annotation(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    # Clear existing annotations to make room for the new ones
    TopicTerms.objects.filter(user=request.user, document=document).delete()

    try:
        for term_id in request.POST.getlist('terms'):
            term = get_object_or_404(Term, pk=term_id)
            topic_term = TopicTerms(user=request.user, document=document, term=term)
            topic_term.save()
    except KeyError:
        return render(request, 'topicterms/annotate.html', {'document': document, 'error_message': 'No terms selected'})

    return HttpResponseRedirect(reverse('topicterms:annotate', args=(document.id,)))
