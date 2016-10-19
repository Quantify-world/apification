from apification.resources import DjangoResource
from apification.actions  import Action

class ListAnswers(DjangoResource):
    writer = AnswerWriter
    
    class List(Action):
        pass

class QuestionResource(DjangoResource):
    writer = QuestionWriter

    class Create(Action):
        method = 'POST'
        reader = CreateQuestionReader
    
    class Get(Action):
        method = 'GET'
        reader = None
    
    class Like(Action):
        method = 'POST'
        reader = LikeQuestionReader

    class List(Action):
        method = 'GET'
        writer = QuestionListWriter

    class Answers(ListAnswers):
        pass


# QuestionResource.Create.resource == QuestionResource

# /answers/ => list of all
# /answers/1/ => id 1
# /questions/33/answers/ => list of Question.objects.get(pk=33).answeroption_set.all()
# /questions/33/answers/1 => 404 if not Answer(pk=1).question == Question.objects.get(pk=33)

# >>>
# POST /questions/ {title:qwe, text: asd}
# <<<
# {id: 1, title: qwe, text:asd, created: 2000-02-01}
