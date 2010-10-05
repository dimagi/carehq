from django.core.management.base import BaseCommand
from optparse import make_option
from casetracker.registry.handler import CategoryHandler
from casetracker.models.casecore import Category


def RegisterHandler(handler_class, update=False, except_on_collision=False):
    handler = handler_class
    print 'Registering Category Handler: ' + handler.category_slug
    exists=False

    cat_qset = Category.objects.filter(slug=handler.category_slug)
    exist_count = cat_qset.count()
    if exist_count > 0 and except_on_collision:
        raise("Error, this category exists, this may be causing instability")
    elif exist_count > 0 and not except_on_collision and update:
        #it exists, don't puke on collisions, then update it foolio
        cat = cat_qset[0]
        cat.display = handler_class.category_display
        cat.description = handler_class.category_description
        cat.save()
    elif exist_count == 0:
        cat = Category()
        cat.slug = handler.category_slug
        cat.display = handler.category_display
        cat.description = handler.category_description
        cat.save()






class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--clean', action='store_true',
                dest='clean_db', default=False,
                help='Override, blow away the Category tables and start anew.'),
        make_option('--replace', action='store_true',
                dest='replace_cat', default=False,
                help='Overwrite any colliding Category'),
    )
    help = 'Load categories by cycling through the CategoryHandler subclasses.'

    def handle(self, *scripts, **options):
        if options.get('clean_db'):
            #not for the faint of heart, this blows away everything
            Category.objects.all().delete()
        if options.get('replace_cat'):
            update=True
        else:
            update=False

        seen = [] #strange it initizliaes it twice
        for cls in CategoryHandler.__subclasses__():
            if seen.count(cls.__name__) != 0:
                continue
            else:
                seen.append(cls.__name__)
            #iterate through all the category handlers and generate new Categories from Scratch
            RegisterHandler(cls, update=update)


