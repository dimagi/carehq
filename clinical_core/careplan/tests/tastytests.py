import uuid
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django_webtest import WebTest
import simplejson
from careplan.models import BaseCarePlan
from permissions.models import Actor, Role, PrincipalRoleRelation
from tenant.models import Tenant

class carePlanAPITests(WebTest):
    def setUp(self):
        User.objects.all().delete()
        Actor.objects.all().delete()
        Role.objects.all().delete()
        PrincipalRoleRelation.objects.all().delete()
        Tenant.objects.all().delete()

        template_careplans = BaseCarePlan.view('careplan/template_careplans', include_docs=True).all()
        for t in template_careplans:
            t.delete()
        call_command('carehq_init')

    def testCreateCarePlanTemplate(self, user=None, actor_type='chw'):
        """
        Create template careplans via tastykit api.
        """
        res = self.app.get(reverse('api_dispatch_list', kwargs={'resource_name': 'TemplateCarePlanResource'}))
        json_content = simplejson.loads(res.content)
        start_count = len(json_content['objects'])

        title = uuid.uuid4().hex

        res = self.app.post(reverse('api_dispatch_list', kwargs={'resource_name': 'TemplateCarePlanResource'}),
            simplejson.dumps({
                'tenant': 'PACT',
                'title': title,
                'description':'foo description',
                "modified_date": "2012-04-16T00:10:50-04:00Z",
                "created_date": "2012-04-16T00:10:50-04:00Z",
                "created_by": "Actor.cea3797889214a1dad679118b692bb7d",
                "modified_by": "Actor.cea3797889214a1dad679118b692bb7d"
            }),
            content_type="application/json",
            status=201,
        )
        created_resource = ""
        for header, val in res.headerlist:
            if header == "Location":
                created_resource = val
                break
        #now GET this resource and verify it exists.
                #http://localhost:80/careplan/api/TemplateCarePlanResource/d1f9771921ea135d56e847ece8c3ef4d/

        r2 = self.app.get(reverse('api_dispatch_list', kwargs={'resource_name': 'TemplateCarePlanResource'}))
        r2_json = simplejson.loads(r2.content)
        self.assertEquals(len(r2_json['objects']), start_count+1)

        r3 = self.app.get("/" + '/'.join(created_resource.split('/')[3:]))
        r3_json = simplejson.loads(r3.content)
        self.assertEquals(r3_json['title'], title)
        return r3_json

    def testEditCarePlanTemplate(self):
        original_json = self.testCreateCarePlanTemplate()
        original_id = original_json['_id']
        original_rev = original_json['_rev']

        edit_json = simplejson.loads(simplejson.dumps(original_json))

        edit_json['title'] = edit_json['title'] + "_EDITED"

        res = self.app.put(reverse('api_dispatch_detail', kwargs={'resource_name': 'TemplateCarePlanResource', 'pk': original_id}), simplejson.dumps(edit_json), content_type="application/json", status=204)
        updated_res = self.app.get(reverse('api_dispatch_detail', kwargs={'resource_name': 'TemplateCarePlanResource', 'pk': original_id}), content_type="application/json")

        updated_json = simplejson.loads(updated_res.content)
        self.assertEquals(edit_json['title'], updated_json['title'])
        self.assertNotEquals(original_json['_rev'], updated_json['_rev'])

    def testDeleteCarePlanTemplate(self):
        pass



    def testAddTemplateItemToTemplate(self):
        pass







