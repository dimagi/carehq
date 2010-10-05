from django.shortcuts import render_to_response
from django.template import RequestContext
from ashandapp.models import CareTeam
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from ashandapp.forms.issue import NewIssueForm
from ashandapp.forms.question import NewQuestionForm

def do_create_case(request, careteam_id, form_class=None, template_name="casetracker/manage/edit_case.html"):
    """
    Wrapper class to help input web/user controlled forms for varying case types.
    
    In order to make a new case form for user input, you must define a subclass of the CareTeamCaseFormBase
    make a new template if you so desire, and make a new method below to handle the form to define/dispatch the correct form classes and templates.
    """    
    context = {}    
    if not form_class:
        raise Exception("Error, you MUST define a form class for this helper method to work")
    
    careteam = CareTeam.objects.get(id=careteam_id)
    context['form'] = form_class(careteam=careteam)
    context['careteam'] = careteam
    if request.method == 'POST':
        form = form_class(data=request.POST, careteam=CareTeam.objects.get(id=careteam_id))
        if form.is_valid():
            newcase = form.get_case(request)        
            newcase.save()
            careteam.add_case(newcase)            
            
            return HttpResponseRedirect(reverse('view-careteam', kwargs= {'careteam_id': careteam_id}))
        else:
            context['form'] = form
    
    return render_to_response(template_name, context, context_instance=RequestContext(request))


#def new_issue(request, careteam_id, template_name="ashandapp/activities/issue/new_issue.html"):
#    return do_create_case(request, careteam_id, form_class=NewIssueForm, template_name=template_name)
#
#def new_question(request, careteam_id, template_name="ashandapp/activities/question/new_question.html"):
#    return do_create_case(request, careteam_id, form_class=NewQuestionForm, template_name=template_name)