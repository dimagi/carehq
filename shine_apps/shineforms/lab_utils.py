

def merge_labs(lab_submissions, as_dict=False):
    """
    """
    sorted_labs = sorted(lab_submissions, key=lambda x: x.received_on)
    hiv = ""
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
        for k,v in submission.form[key].items():
            if k not in ret_dict:
                ret_dict[k] = ''
            stored_val = ret_dict[k]
            if stored_val == "" and v != "":
                ret_dict[k] = v
        return ret_dict


    for sub in lab_submissions:
        if sub.form['hiv'] != "":
            hiv = sub.form['hiv']
        if sub.form['rapid'] != "":
            mal_rapid = sub.form['rapid']
        if sub.form['smear'] != "":
            mal_smear = sub.form['smear']
        if sub.form.get('prophylaxis', '') != "":
            prophylaxis = sub.form['prophylaxis']
        if sub.form['afb_smear'] != "":
            afb_smear = sub.form['afb_smear']
        if sub.form['xray'] != "":
            if sub.form['xray'] == 'other':
                if 'xrayother' in sub.form:
                    xray = "Other: %s" % sub.form['xrayother']
                else:
                    xray='other'
            else:
                xray = sub.form['xray']

        if 'bloodwbc' in sub.form:
            bloodwbc = fill_sub_dict(sub, 'bloodwbc')
        if 'hivfollowup' in sub.form:
            hivfollowup = fill_sub_dict(sub, 'hivfollowup')
        if 'bloodcts' in sub.form:
            bloodcts = fill_sub_dict(sub, 'bloodcts')

    if as_dict:
        return {
                'hiv': {'hiv_test': hiv, 'followup': hivfollowup},
                'malaria': {'rapid': mal_rapid, 'smear': mal_smear},
                'prophylaxis': prophylaxis,
                'afb_smear': afb_smear,
                'xray': xray,
                'bloodwbc': bloodwbc,
                'hemogram': bloodcts,
                'lft': {},
        }
    else:
        return [
            ('hiv', { 'hiv test': hiv, 'followup': hivfollowup}),
            ('malaria', {'rapid': mal_rapid, 'smear': mal_smear}),
            ('prophylaxis', prophylaxis),
            ('afb_smear', afb_smear),
            ('xray', xray),
            ('bloodwbc', bloodwbc),
            ('hemogram', bloodcts),
            ('lft', dict()),
        ]