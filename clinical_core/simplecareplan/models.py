from django.db import models
from django.contrib.auth.models import User
from clinical_core.actors.models.roles import Actor
from tinymce import models as tinymce_models


class CarePlanElement(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField(blank=True,null=True)

    def __unicode__(self):
        return "Care Plan Element: " + self.name

class CarePlan(models.Model):
    patient = models.ForeignKey(Actor, unique=True, related_name="careplan_patient")
    text = tinymce_models.HTMLField(blank=True,null=True)
    elements = models.ManyToManyField(CarePlanElement, blank=True, null=True)
    last_edited_by = models.ForeignKey(Actor, unique=True)

    def __unicode__(self):
        return "Care Plan: " + self.patient.username

    
    
    