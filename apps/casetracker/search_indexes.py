from haystack.indexes import *
from haystack import site
from casetracker.models import *


class CaseIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

site.register(Case, CaseIndex)
