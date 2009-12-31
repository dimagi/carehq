from django.shortcuts import render_to_response

 
def styleguide(request, template_name="ashandapp/styleguide.html"):
    context = {}
    return render_to_response(template_name, context)
