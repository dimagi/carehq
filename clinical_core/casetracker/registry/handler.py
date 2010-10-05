

class CategoryHandler(object):
    """
    A CategoryHandler is a wrapper class that enables you to bootstrap your application.

    If your database is empty, it'll populate a Category with the slug and other data below to create your custom category.
    """

    category_slug = None
    category_display = None
    category_description = None

    custom_create = False
    custom_read = False

    states = []
    activities = []


    def __init__(self, initialize=False, *args, **kwargs):
        if self.category_slug == None:
            raise Exception("Error, you must specify a slug to match the entry to appear in the Category model table")
        if self.category_display == None:
            raise Exception("Error, you must specify a display string to match the entry to appear in the Category model table")
        if self.category_plural == None:
            raise Exception("Error, you must specify a plural string to match the entry to appear in the Category model table")

        if self.bridge_class == None:
            raise Exception("Error, you must specify a class to match the entry to appear in the Category model table")
        if self.bridge_module == None:
            raise Exception("Error, you must specify a module to match the entry to appear in the Category model table")

    def create_template(self, request, context, *args, **kwargs):
        """
        The create template is the template path you will use when calling the view function
        to create a new case.  This includes rendering the Form class and the actual layout of the fields on the browser.
        """
        return 'casetracker/manage/edit_case.html'
    def create_context(self, request, context, *args, **kwargs):
        """
        The create_context is a function to populate any additional context variables for your create view
        """
        return context
    def create_viewfunc(self, request, context, *args, **kwargs):
        """
        An optional override to completely override the default castracker.view create view function.
        """
        if not self.custom_create:
            raise Exception("Error, this handler class is not configured to use a custom view class")
        return None

    def read_template(self, request, context, *args, **kwargs):
        return 'casetracker/manage_case.html'
    def read_context(self, case, request, context, *args, **kwargs):
        context['case'] = case
        return context
    def read_viewfunc(self, case, request, context, *args, **kwargs):
        """
        If a wholesale view override is desired, just implement it here.
        """
        if not self.custom_read:
            raise Exception("Error, this category handler class is not configured to use a custom view class")
        return None
    def get_user_list_choices(self, case):
        return None
