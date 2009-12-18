from datetime import datetime, timedelta
import hashlib
from django.contrib.auth.models import User
from casetracker.models import Case, Status, EventActivity, CaseEvent, Priority, Category, CaseAction
import random

MAX_DELTA=365

def create_user(username='mockuser', password='mockmock'):    
    user = User()    
    user.username = username
    # here, we mimic what the django auth system does
    # only we specify the salt to be 12345
    salt = '12345'
    hashed_pass = hashlib.sha1(salt+password).hexdigest()
    user.password = 'sha1$%s$%s' % (salt, hashed_pass)
    
    user.set_password(password)
    user.save()
    return user


def create_case(user, case_no):    
    newcase = Case()
    newcase.description = "test case generated - %d" % case_no
    newcase.opened_by = user
    
    newcase.category = Category.objects.all()[random.randint(0, Category.objects.all().count()-1)]
    newcase.status = Status.objects.all()[random.randint(0, Status.objects.all().count() -1)]
    newcase.priority = Priority.objects.all()[random.randint(0, Priority.objects.all().count() -1)]    
    newcase.next_action = CaseAction.objects.all()[random.randint(0, CaseAction.objects.all().count() -1)]
    
    td = timedelta(days=random.randint(0,MAX_DELTA))
    newcase.next_action_date = datetime.utcnow() + td
    
    newcase.save()
    return newcase

def modify_case(case, user, rev_no):    
    case.description = "modified by %s - rev %d" % (user.username, rev_no)
    case.last_edit_by = user
    
    case.next_action = CaseAction.objects.all()[random.randint(0, CaseAction.objects.all().count() -1)]
    td = timedelta(days=random.randint(0,MAX_DELTA))    
    case.next_action_date = case.next_action_date + td
    case.save()        

def run():
    users = []
    NUM_USERS=20
    MAX_REVISIONS=10
    MAX_INITIAL_CASES = 100
    #first, create users
    try:
        for num in range(0,NUM_USERS):
            username = "user%d" % num
            password = "mock%d" % num
            users.append(create_user(username=username, password=password))
            print "Created user %s" % username
    except:
        users=User.objects.all()
        NUM_USERS = User.objects.all().count()
        pass
    
    print "Mock user creation completed\n"
    print "Generating cases\n"
    #next, create a crap load of cases
    revision_no = 0
    for num in range(0,MAX_INITIAL_CASES):
        case = create_case(users[random.randint(0,NUM_USERS-1)], num)
        num_revisions = random.randint(0,MAX_REVISIONS)
        #next, do an arbitrary number or revisions     
        print "Case created"   
        for rev in range(0,num_revisions):
            print "\tApplying revision %d - %d" % (rev, revision_no)
            modding_user = users[random.randint(0,NUM_USERS-1)]
            modify_case(case, modding_user, revision_no)
            revision_no += 1
        
        
        

    
    
        
        
        
        
        