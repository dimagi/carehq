from haystack.indexes import *
from haystack import site
from issuetracker.models import *


class CaseIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

site.register(Issue, CaseIndex)
