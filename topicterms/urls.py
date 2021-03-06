from django.urls import path

from . import views


app_name = 'topicterms'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('annotate/<int:pk>/', views.AnnotateView.as_view(), name='annotate'),
    path('annotate/<int:document_id>/record', views.record_annotation, name='record_annotation'),
    path('annotate/<int:document_id>/skip', views.skip_annotation, name='skip_annotation'),
    path('document/<int:pk>/', views.DocumentView.as_view(), name='document'),
]