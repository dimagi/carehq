

class CategoryHandlerBase(object):
    """
    A CategoryHandler is a base class that allows a case of an arbitrary category
    to be dispatched to an appropriate handler for rendering its template
    """
    
    def __init__(self):
        
        #activities must be a tuple of (name, summary, event-class (from constants), phrasing)
        self.activities = []
        
        #status must be (description, state-class)
        self.status = []
    
    def get_form(self):
        pass
    
    def get_view_template(self):
        pass
    
    def process_context(self, case, request, context, *args, **kwargs):
        """
        Sets additional context variables when processing this case in a view
        """
        context['can_edit'] = True
        context['can_assign'] = True
        context['can_resolve'] = True
        context['can_close'] = True
        return context
    
    def get_user_list_choices(self, case):
        return None
    #lifecycle management?



class DefaultCategoryHandler(CategoryHandlerBase):
    def get_form(self):
        #hacky but this pukes on bootstrap loading
        from casetracker.forms import CaseModelForm
        return CaseModelForm
    
    def get_view_template(self):
        return "casetracker/manage_case.html"
    
    def process_context(self, case, request, context, *args, **kwargs):
        return context
    
    def get_user_list_choices(self, case):
        return None
        