import simplejson

def merge_labs(lab_submissions, as_dict=False):
    """
    """
    sorted_labs = sorted(lab_submissions, key=lambda x: x['received_on'])
    hiv_status = ""
    mal_rapid = "" #rapid
    mal_smear = "" #smear
    prophylaxis = ""
    afb_smear = ""
    bloodwbc =dict()
    xray = ""
    hivfollowup = dict()
    bloodcts = dict()

    basic_chemistry = dict()
    lft = dict()

    def fill_sub_dict(submission, key):
        ret_dict = dict()
        for k,v in submission['form'][key].items():
            if k not in ret_dict:
                ret_dict[k] = ''
            stored_val = ret_dict[k]
            if stored_val == "" and v != "":
                ret_dict[k] = v
        return ret_dict

    hiv_test_done = 'no'

    for sub in lab_submissions:

        #old style checks
        if sub['form']['hiv'] != "":
            hiv_status = sub['form']['hiv']
        if sub['form']['rapid'] != "":
            mal_rapid = sub['form']['rapid']
        if sub['form']['smear'] != "":
            mal_smear = sub['form']['smear']
        if sub['form'].get('prophylaxis', '') != "":
            prophylaxis = sub['form']['prophylaxis']
        if sub['form']['afb_smear'] != "":
            afb_smear = sub['form']['afb_smear']
        if sub['form']['xray'] != "":
            if sub['form']['xray'] == 'other':
                if 'xrayother' in sub['form']:
                    xray = "Other: %s" % sub['form']['xrayother']
                else:
                    xray='other'
            else:
                xray = sub['form']['xray']

        if 'bloodwbc' in sub['form']:
            bloodwbc = fill_sub_dict(sub, 'bloodwbc')
        if 'hiv_followup' in sub['form']:
            hivfollowup = fill_sub_dict(sub, 'hiv_followup')
        if 'bloodcts' in sub['form']:
            bloodcts = fill_sub_dict(sub, 'bloodcts')


        if sub['form'].has_key('sections'):
            #new style checks
            for labkey, val in sub['form']['sections'].items():
                if labkey == 'labs_xray':
                    #done: yes/no
                    xray = val
                if labkey == 'labs_wbc':
                    #["blood_neutrophils", "blood_lymphocytes", "@name", "blood_eosinophils", "done", "blood_monocytes", "blood_wbc"]
                    bloodwbc = val
                if labkey == 'labs_prophylaxis':
                    #done: yes/no
                    prophylaxis = val['done']
                if labkey == 'labs_malaria':
                    #done: yes/no
                    if val['done'] == u'no':
                        mal_rapid = 'no'
                    elif val['done'] is dict:
                        mal_rapid = 'done'
                        #need to get value from malaria data?
                if labkey == 'labs_liver_func':
                    #["blood_tp", "@name", "blood_alt", "blood_alb", "blood_ast", "done", "blood_dir_bili", "blood_tbili"]
                    lft = val
                if labkey == 'labs_hivstatus':
                    #done: yes/no
                    if val['done'] == 'no':
                        hiv_test_done = 'no'
                    elif val['done'] == 'done':
                        hiv_test_done = 'done'
                    elif val['done'] == '':
                        hiv_test_done = 'no'
                    else:
                        #this is suuuuper sketchy but we're getting the hashed dict stuff here.
                        valdict = eval(val['done'])
                        hiv_test_done = valdict['#text']
                if labkey == 'labs_hemogram':
                    #["done", "blood_hgb", "@name", "blood_plts", "blood_mcv"]
                    bloodcts = dict(bloodcts.items() + val.items())
                if labkey == 'labs_basic_chem':
                    #["blood_na", "blood_k", "blood_cr", "@name", "blood_glucose", "done", "blood_cl"]
                    bloodcts = dict(bloodcts.items() + val.items())
                    pass
                if labkey == 'labs_afb_smear':
                    #done: yes/no
                    afb_smear = val['done']


    if as_dict:
        return {
                'hiv': {'hiv_status': hiv_status, 'followup': hivfollowup, 'tested': hiv_test_done},
                'malaria': {'rapid': mal_rapid, 'smear': mal_smear},
                'prophylaxis': prophylaxis,
                'afb_smear': afb_smear,
                'xray': xray,
                'bloodwbc': bloodwbc,
                'hemogram': bloodcts,
                'lft': lft,
        }
    else:
        return [
            ('hiv', { 'hiv test': hiv_status, 'followup': hivfollowup, 'tested': hiv_test_done}),
            ('malaria', {'rapid': mal_rapid, 'smear': mal_smear}),
            ('prophylaxis', prophylaxis),
            ('afb_smear', afb_smear),
            ('xray', xray),
            ('bloodwbc', bloodwbc),
            ('hemogram', bloodcts),
            ('lft', lft),
        ]