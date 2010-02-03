from casetracker.CategoryHandler import CategoryHandlerBase
from ashandapp.forms.question import NewQuestionForm
from ashandapp.forms.issue import NewIssueForm

class QuestionHandler(CategoryHandlerBase):
    def get_form(self):
        return NewQuestionForm
    
    def get_view_template(self):
        return "ashandapp/cases/view_question.html"



class IssueHandler(CategoryHandlerBase):
    def get_form(self):
        return NewIssueForm
    
    def get_view_template(self):
        return "ashandapp/cases/view_issue.html"

