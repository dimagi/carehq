from xml.etree import ElementTree
from casexml.apps.case.xml import V2
from pactcarehq.models import PactUser

PACT_HP_GROUP_NAME = "PACT-HPS"
PACT_HP_GROUP_ID = "ee042f33c890421794f69ed81e030882"

def pact_hp_group(user, version=V2, last_sync=None):
    if isinstance(user, PactUser):
        pass
    else:
        return []

    fixtures = []

    xFixture = ElementTree.Element('fixture', attrib={'id': 'user-groups', 'user_id': user.user_id})
    xGroups = ElementTree.SubElement(xFixture, 'groups')

    xGroup = ElementTree.SubElement(xGroups, 'group', attrib={'id': PACT_HP_GROUP_ID})
    xName = ElementTree.SubElement(xGroup, 'name')
    xName.text = PACT_HP_GROUP_NAME
    fixtures.append(xFixture)
    return fixtures