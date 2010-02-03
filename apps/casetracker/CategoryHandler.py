

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
    
    
    
    
    #lifecycle management?



class DefaultCategoryHandler(CategoryHandlerBase):
    def get_form(self):
        #hacky but this pukes on bootstrap loading
        from casetracker.forms import CaseModelForm
        return CaseModelForm
    
    def get_view_template(self):
        return "casetracker/view_case.html"