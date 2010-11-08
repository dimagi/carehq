from casetracker.models import Case


def get_sorted_caseevent_dictionary(sort, arr):
    sorted_dic = {} #sorted dictionary of organized events for newsfeed
    obj = None 
        
    if (sort == "person"): 
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.created_by.title()):
                    sorted_dic[obj.created_by.title()] = []
                sorted_dic[obj.created_by.title()].append(obj)
            elif obj.created_by.title() == event.created_by.title():
                sorted_dic[obj.created_by.title()].append(event)
            else :
                obj = event
                if not sorted_dic.has_key(obj.created_by.title()):
                    sorted_dic[obj.created_by.title()] = []
                sorted_dic[obj.created_by.title()].append(obj)
    elif (sort == "category"): 
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.activity.category.slug):
                    sorted_dic[obj.activity.category.slug] = []
                sorted_dic[obj.activity.category.slug].append(obj)
            elif obj.activity.category.slug == event.activity.category.slug:
                sorted_dic[obj.activity.category.slug].append(event)
            else :
                obj = event
                if not sorted_dic.has_key(obj.activity.category.slug):
                    sorted_dic[obj.activity.category.slug] = []
                sorted_dic[obj.activity.category.slug].append(obj)
    elif (sort == "activity"):            
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.activity.past_tense.title()):
                    sorted_dic[obj.activity.past_tense.title()] = []
                sorted_dic[obj.activity.past_tense.title()].append(obj)
            elif obj.activity.past_tense.title() == event.activity.past_tense.title():
                sorted_dic[obj.activity.past_tense.title()].append(event)                
            else :
                obj = event
                if not sorted_dic.has_key(obj.activity.past_tense.title()):
                    sorted_dic[obj.activity.past_tense.title()] = [] 
                sorted_dic[obj.activity.past_tense.title()].append(obj)                
    elif (sort == "case"):            
        for event in arr:
            if (obj == None):
                obj = event
                if not sorted_dic.has_key(obj.case.case_name_url()):
                    sorted_dic[obj.case.case_name_url()] = []
                sorted_dic[obj.case.case_name_url()].append(obj)
            elif obj.case.id == event.case.id:
                sorted_dic[obj.case.case_name_url()].append(event)                
            else :
                obj = event
                if not sorted_dic.has_key(obj.case.case_name_url()):
                    sorted_dic[obj.case.case_name_url()] = [] 
                sorted_dic[obj.case.case_name_url()].append(obj) 
    
    return sorted_dic
