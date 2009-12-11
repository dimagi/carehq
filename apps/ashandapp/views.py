from django.shortcuts import render_to_response
from datagrids import UserDataGrid
 
def datagrids(request, template_name='ashandapp/datagrids.html'):
    return UserDataGrid(request).render_to_response(template_name)

def styleguide(request, template_name="ashandapp/styleguide.html"):
    context = {}
    return render_to_response(template_name, context)