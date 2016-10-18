from django.conf.urls import url, include

from qa.api import QuestionResource

urlpatterns = [
    url('', include(QuestionResource.urls)),
]
