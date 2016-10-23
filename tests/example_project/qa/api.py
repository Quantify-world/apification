from apification.resources import DjangoResource
from apification.collections import DjangoCollection
from apification.actions  import Action
from apification.readers import Reader
from apification.writers import Writer

from qa.models import Question


class AnswerWriter(Writer):
    pass
class QuestionWriter(Writer):
    pass
class LikeQuestionReader(Reader):
    pass

class ListAnswers(DjangoCollection):
    writer = AnswerWriter
    
    class List(Action):
        pass


class QuestionLikeAction(Action):
    method = 'POST'
    reader = LikeQuestionReader


class QuestionCollection(DjangoCollection):
    name = 'questions'
    model = Question
    
    class Create(Action):
        method = 'POST'

    class Purge(Action):
        method = 'DELETE'

    class Item(DjangoResource):
        writer = QuestionWriter
        name = 'question'

        def get_queryset(self, request):
            return Question.objects.all()
    
        class Get(Action):
            method = 'GET'
            def run(self):
                from django import http
                return http.HttpResponse(unicode((self.args, self.kwargs)))

        class Ping(Action):  # example action
            method = 'POST'
    
        class Like(DjangoResource):
            Post = QuestionLikeAction
    
            class Delete(Action):
                method = 'POST'
    
        class Answers(ListAnswers):
            pass

# QuestionResource.Create.resource == QuestionResource

# GET /answers/ => list of all
# GET /answers/1/ => id 1
# GET /questions/33/answers/ => list of Question.objects.get(pk=33).answeroption_set.all()
# GET /questions/33/answers/1 => 404 if not Answer(pk=1).question == Question.objects.get(pk=33)

# POST /question/1/like/
# DELETE /question/1/like/

# LIKE /question/1/
# DELETE_LIKE /question/1/like/

# POST /question/1/likes/34/
# DELETE /question/1/likes/34/
# GET /question/1/likes/

# >>>
# POST /questions/ {title:qwe, text: asd}
# <<<
# {id: 1, title: qwe, text:asd, created: 2000-02-01}
