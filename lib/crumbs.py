from django.core.urlresolvers import reverse
from functools import wraps

hierarchy = { } # This is a global variable.  It's OK to use it because it's essentially static at runtime.

def walk_hierarchy(name, iters=0):
    if iters > 100:
        raise Exception("Circular parent reference detected")
    if name in hierarchy:
        return walk_hierarchy(hierarchy[name]["parent"], iters=iters + 1) + [[hierarchy[name]["name"], reverse(name)]]
    elif name is not None:
        # Page doesn't exist yet?  Try to import it.
        reverse(name) # Hack to walk urlconfs
        if not name in hierarchy:
            return []
        else:
            return walk_hierarchy(name, iters)
    else:
        return []


def crumbs(name, layout_name, parent):
    if not layout_name in hierarchy:
        hierarchy[layout_name] = {"name":name, "parent":parent}
    elif hierarchy[layout_name]["name"] != name or hierarchy[layout_name]["parent"] != parent:
        raise Exception("Attempt to redefine existing hierarchy entry " + layout_name)
    def factory(f):
        @wraps(f)
        def wrapped(request, *args, **kwargs):
            request.breadcrumbs(walk_hierarchy(layout_name))
            return f(request, *args, **kwargs)
        return wrapped
    return factory
    