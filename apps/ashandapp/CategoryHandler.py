from casetracker.forms import CaseModelForm, CaseCommentForm, CaseResolveCloseForm
from casetracker.CategoryHandler import CategoryHandlerBase, DefaultCategoryHandler
from ashandapp.forms.question import NewQuestionForm
from ashandapp.forms.issue import NewIssueForm
from careplan.models import TemplateCarePlan

from django.contrib.auth.models import User

def process_ashand_case(case, request, context):
    context['can_edit'] = False
    context['can_assign'] = False
    context['can_resolve'] = False
    context['can_close'] = False
    
    if request.user == case.opened_by:
        context['can_edit'] = True
        
    if request.is_provider:
        context['can_assign'] = True
        context['can_resolve'] = True
        context['can_close'] = True
    
    context['case_careteams'] = case.careteam_set.all()
    context['careplan'] = TemplateCarePlan.objects.all()[0]
    context['plan_items'] = context['careplan'].templatecareplanitemlink_set.all()
    context['show_children'] = True
     
    
    return context

def do_get_user_list_choices(case):
    careteams = case.careteam_set.all()
    providers_users = User.objects.none()
    caregivers_users = User.objects.none()

    #get the split ids of users for caregivers and providers
    for ct in careteams:
        providers_qset = ct.providers.all().values_list('user__id', flat=True)
        providers_users = providers_users | User.objects.filter(id__in=providers_qset)
        
        caregivers_qset = ct.caregivers.all().values_list('id', flat=True)
        caregivers_users = caregivers_users | User.objects.filter(id__in=caregivers_qset)
    
    
    
    #make the optgroup tuples
    #source: http://dealingit.wordpress.com/2009/10/26/django-tip-showing-optgroup-in-a-modelform/
    prov_tuple = [[usr.id, usr.get_full_name()] for usr in providers_users.order_by('last_name')]
    cg_tuple = [[usr.id, usr.get_full_name()] for usr in caregivers_users.order_by('last_name')]

    list_choices = [['Providers', prov_tuple],
                    ['Caregivers',cg_tuple]]
                                    
    return list_choices

class QuestionHandler(CategoryHandlerBase):
    def get_form(self):
        return NewQuestionForm
    
    def get_view_template(self):
        return "ashandapp/cases/view_question.html"
    
    def get_user_list_choices(self, case):
        return do_get_user_list_choices(case)

    def process_context(self, case, request, context, *args, **kwargs):
        return process_ashand_case(case, request, context)


class IssueHandler(CategoryHandlerBase):
    def get_form(self):
        return NewIssueForm
    
    def get_view_template(self):
        return "ashandapp/cases/view_issue.html"

    def get_user_list_choices(self, case):
        return do_get_user_list_choices(case)

    def process_context(self, case, request, context, *args, **kwargs):
        return process_ashand_case(case, request, context)
    
class HomeMonitoringHandler(DefaultCategoryHandler):
    def get_view_template(self):
        return "ashandapp/cases/view_home_monitoring.html"

    def get_user_list_choices(self, case):
        return do_get_user_list_choices(case)

    def process_context(self, case, request, context, *args, **kwargs):
        return process_ashand_case(case, request, context)


class SystemCaseHandler(DefaultCategoryHandler):
    def get_view_template(self):
        return "ashandapp/cases/view_system_case.html"

    def get_user_list_choices(self, case):
        return do_get_user_list_choices(case)

    def process_context(self, case, request, context, *args, **kwargs):
        return process_ashand_case(case, request, context)
