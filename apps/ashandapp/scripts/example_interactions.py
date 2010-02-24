#format needs to be:
#[category, body, source, responsetext1,responsefrom2,responsetype2, 
#
#
#]

#each element in the array represents one sequence of issues
interactions_arr = [
["question","How do I get patient's appetite back?","Just concerned that with the nausea and weakness, she'll lose even more weight.","caregiver","I'm going to loop in a eating specialist for our next conversation.","provider","comment","Can you provide me the last few meals the patient had?","provider","comment","","","","","","","","",""],
["question","How long will the next visit last?","I need to get back for another meeting that came up","patient","The next visit is 20 minutes clinical, 60 minute therapy.  Please plan for 2 hours.","provider","Resolve","","","","","","","","","","","",""],
["issue","%s has headache that is not relieved by Tylenol","It's a 7 on the scale of 1-10","Caregiver","So long as there is no fever, we may need to ride this one out.","provider","Resolve","","","","","","","","","","","",""],
["issue","Fingernail color has been changing","Haven't seen it yet, will do soon","Caregiver","The visiting nurse looks to be visiting in the next 24 hours, I will instruct them to take a closer look at that region.","provider","Resolve","","","","","","","","","","","",""],
["issue","Bleeding gums","was about to brush my teeth when I saw it","patient","The visiting nurse looks to be visiting in the next 24 hours, I will instruct them to take a closer look at that region.","provider","Resolve","","","","","","","","","","","",""],

["question","Feeling rising pain in sternum","I think it's the sternum, somewhere on my chest","patient","Let's follow this up at the next visit.  For now it's something we'll consider normal.","provider","comment","Ok.  It's been a little while later and it's come down.","caregiver","comment","","","","","","","","",""],
["question","Patient is unable to afford food","the high calorie diet is hard to maintain","caregiver","I've given a call to meals on wheels, expect a call from them.","provider","Resolve","","","","","","","","","","","",""],
["question","Can other caregivers and loved ones be present at %s's next visit?","I'm %s's ride,but also I'm the defacto translator","caregiver","Yes, feel free to come.","provider","Resolve","","","","","","","","","","","",""],
["question","Will health insurance cover next round of prescriptions?","Just concerned about the affordability","caregiver","All medications that we provide in the clinic are covered under the patient's insurance policy","provider","Resolve","","","","","","","","","","","",""],


["question","How do I prevent recurring mouth sores?","They seem to keep popping up and bothering her quite often.","patient","There are several topical treatments you can try.  Please see http://www.emedicinehealth.com/canker_sores/article_em.htm","provider","comment","Yeah, I tried those, but they didn't seem to fit the patient's description.","caregiver","comment","Interesting.  If it persists to unbearable levels, let's schedule an appointment asap.","provider","comment","","","","","",""],
["question","%s is constantly complaining of nausea, doesn't she have meds for that?!","Anything please, it's almost a daily occurrence.","caregiver","Can you verify that ALL the medications for their anti nausea meds are being taken?  They are specially tailored for the nasuea side effects of the chemo they are on.  If they are taking them to the letter, then we will need to arrange an appointment to adjust their dosage.","provider","comment","Ah, ok come to think of it, the patient just told me they hadn't been taking them all in sequence.  I'll get back to you once she tries to follow them to the letter.","caregiver","comment","","","","","","","","",""],
["question","When should the patient get vaccinated for H1N1?","Any word on availability?","patient","Immediately - we have already put her on the front of the waiting queue - cancer patients are high risk for contracting the disease.","provider","Resolve","","","","","","","","","","","",""],
["question","Patient weight","How frequently should I be monitoring the patient's weight","caregiver","Please instruct the patient to use the home monitoring device daily.  ","provider","Resolve","","","","","","","","","","","",""],
["question","Should I eat before next visit?","I hear that there's some labs to be done, should I fast for those?","patient","No, they should fast before the next visit","provider","Resolve","","","","","","","","","","","",""],
["question","Will patient be able to drive by themselves to and from next visit?","The next visit will involve a strong chemo dosage, so the side effects will not be pleasant.","provider","I will be taking the patient to the visit myself","caregiver","Resolve","","","","","","","","","","","",""],
["question","Is oral chemotherapy taken by itself, or with other treatments?","Will food cause it to lose effectiveness?","patient","If %s is able to keep food down, then by all means take with food.","provider","Resolve","","","","","","","","","","","",""],
["question","How much grace period is there for me to take my medicine around the scheduled time?","Are these things like antibiotiics and they need to be always in a certain schedule?","caregiver","Please try to be as prompt and regulated as possible.","provider","Resolve","","","","","","","","","","","",""],
#["question","I'm noticing %s seems to be rapidly gaining weight","I don't notice any altered diet","caregiver","Make sure %s is doing the daily home monitoring measurements, if the weight gain is that rapid, the visiting nurse will contact you.","provider","Resolve","","","","","","","","","","","",""],
["question","%s seems to be rapidly losing weight","I don't notice any altered diet","caregiver","Make sure the %s is doing the daily home monitoring measurements, if the weight gain is that rapid, the visiting nurse will contact you.","provider","Resolve","","","","","","","","","","","",""],
["question","I'm noticing %s has trouble hearing me, is this temporary?","Is this part of the side effects?  I don't see it in the care plan","caregiver","If the symptoms worsen over the next 48 hours please come in immediately.","provider","Resolve","","","","","","","","","","","",""],
["question","My skin is going crazy, help!","it's red and rashed, but dry in other spots","patient","Please see the care plan on skin side effects - if the issues persist and match the high severity scenarios, please come in.","provider","comment","Yeah, I tried those, but even the ones that fit the patient's symtoms don't seem to provide any relief!","caregiver","","","","","","","","","",""],
["question","%s keeps mentioning abnormal muscle weakness, anything more I can do?  ","I know she's not exactly active, but she's not sedentary either.","caregiver","Unfortunately this is a normal side effect.  There are ways to combat it to give the patient some normalcy to their routines.  Please see the care plan on fatigue management.","provider","Resolve","","","","","","","","","","","",""],
["issue","%s is complaining of shaking chills","Just got off the phone and that's what she was saying, I'm stopping by later today, what should I look out for?","Caregiver","If there is no fever, then this may be normal.","provider","Resolve","no fever, I think we can wait on this for a bit","caregiver","","","","","","","","","",""],
["issue","Bleeding or bruising","I noticed the other day that on legs and arms it's pretty badly bruised","patient","Let's see how they heal in the next few days, if they persist, I will examine at the next visit, so long as they don't spread and get bigger, if that's the case come in immediately.","provider","Resolve","","","","","","","","","","","",""],
["issue","%s has severe constipation or diarrhea","Just happened today from what %s told me.","Caregiver","Please see the updated care plan on GI issues.","provider","Resolve","","","","","","","","","","","",""],
["issue","It hurts to go to the bathroom","please help","patient","Please see the updated care plan on GI issues.","provider","Resolve","","","","","","","","","","","",""],
["issue","%s has red urine","%s just called me, she's very worried.","Caregiver","This is a normal side effect of the chemo, please advise to drink a lot of fluids.","provider","Resolve","","","","","","","","","","","",""],
["issue","Patient has soreness, redness, swelling, pus, or drainage at VAD site","Anything I can do to help?","Caregiver","Instructing visiting nurse to take a second look at dressings","provider","Resolve","","","","","","","","","","","",""],
["issue","Irregular or rapid heart beat","Has just happened, what's going on?","patient","If there is a fever, then call 911.","provider","Resolve","","","","","","","","","","","",""],
["issue","Patient has pain that is not relieved by prescribed pain medication.","It's a 7 on the scale of 1-10","Caregiver","Consider other OTC pain relief like Tylenol or Advil","provider","Resolve","","","","","","","","","","","",""],
["issue","Patient has inability to eat and continued weight loss","No vomiting per se, but no appetite","Caregiver","Let's keep an eye on the weight loss.","provider","Resolve","","","","","","","","","","","",""],
["issue","more mouth sores appearing","Just happened last night","patient","There are several topical treatments you can try.  Please see http://www.emedicinehealth.com/canker_sores/article_em.htm","provider","Resolve","","","","","","","","","","","",""],
["issue","%s has nasal congestion, drainage, cough","%s is feeling pretty miserable.  Hard to tell if there is any additional weakness since that's just the general feeling now.","Caregiver","These may be signs of other infections.  Please see care plan on infections and monitor %s's temperature closely for any signs of fever.","provider","Resolve","","","","","","","","","","","",""],
["issue","Abnormally high dizziness and lightheadedness when standing","Pretty recent turn of events","Caregiver","Unfortunately this is normal, if it persists, let's bring it up as a talking point for next appointment","provider","Resolve","","","","","","","","","","","",""],
["issue","Noticing abnormal swelling at IV site","Haven't seen it yet, will do soon","Caregiver","The visiting nurse looks to be visiting in the next 24 hours, I will instruct them to take a closer look at that region.","provider","Resolve","","","","","","","","","","","",""],
["issue","There's Redness at IV site","not itchy though","patient","The visiting nurse looks to be visiting in the next 24 hours, I will instruct them to take a closer look at that region.","provider","Resolve","","","","","","","","","","","",""],
["issue","Chronic itching","Has been getting progressively worse","patient","See care plan on skin conditions","provider","Resolve","","","","","","","","","","","",""],
["issue","Patient is complaining of consistent ringing in ears","Has been getting progressively worse","Caregiver","See care plan on skin conditions","provider","Resolve","","","","","","","","","","","",""],
["HomeMonitoring","Patient weight has dropped over 10 lbs","Daily reading reported.","Home Monitor","I scheduled a visit for the patient to come in this week","provider","Resolve","","","","","","","","","","","",""],
["HomeMonitoring","Patient has been vomiting more than 48 hours after treatment","Number of times: 3, has taken all anti emetics.","Home Monitor","Unfortunately, this is normal for the treatment given, if it persists, we will need to adjust the anti nausea meds.","provider","Resolve","","","","","","","","","","","",""],
["HomeMonitoring","Patient has shortness of breath/chest pain","Onset: 12 hours ago","Home Monitor","Call made to patient, advised to come visit if the severity increases.","provider","Resolve","","","","","","","","","","","",""],
["HomeMonitoring","Patient has pain in a new place","Location: lower back","Home Monitor","Patient called and discussed pain.  OTC Advil recommended","provider","Resolve","","","","","","","","","","","",""],
["HomeMonitoring","Patient has severe nausea","Severity: high, no vomiting","Home Monitor ","Patient switched to Anzemet ","provider","Resolve","","","","","","","","","","","",""],
["HomeMonitoring","Patient is experiencing hearing loss","Onset: 3 hours ago.  Partial hearing loss in left ear","Home Monitor","Patient instructed to come in or visit","provider","Resolve","","","","","","","","","","","",""],
#["HomeMonitoring","Patient has not submitted daily measurements","Missing data alert","Home Monitor","Call made to patient, contact made","provider","Resolve","","","","","","","","","","","",""],
["HomeMonitoring","Patient daily measurements incomplete","Missing data alert","Home Monitor","Call made to patient, contact made","provider","Resolve","","","","","","","","","","","",""],
]


triage_arr = [
["issue","hi, regarding %s","%s is reporting that they have not had a BM in over 2 days now.","Caregiver"],
["HomeMonitoring","Patient has vomited 2 times in the past 24 hours","Daily reading alert","Home Monitor"],
["issue","urgent","What order should I instruct the patient to take their anti nausea meds?","Caregiver"],
#["HomeMonitoring","Patient has not submitted daily measurements","Missing data alert","Home Monitor"],
["issue","help","Do I need to fast before my next visit?","patient"],
["issue","not feeling well","%s has been reporting severe nausea the past few days","Caregiver"],
["issue","more skin problems for %s","Thanks for the tip on the last skin issue!","caregiver"],
["issue","%s has a runny nose","is it bad?","Caregiver"],
["issue","fever","at what temperature should I know to call for help?","patient"],
#["issue","diarrhea?","%s said it feels like it's happening but it is a normal movement - anything to help avoid?","Caregiver"],
["issue","%s has severe diarrhea","%s was up most of the night, was able to stay hydrated, but am worried.","Caregiver"],
["HomeMonitoring","Patient daily measurements incomplete","Missing data alert","Home Monitor"],
["issue","is it bad?","not sure if this is hives or a rash","Caregiver"],
["issue","%s told me yesterday that it's really difficult to climb the stairs as she is completely winded after a few steps.  Is this normal?","ok, thanks.","Caregiver"],
]


long_cases = [
              ["issue","Patient is complaining of constipation","She says it's been almost 2 days since her last BM","caregiver","Does she have any feeling of gas or pain?  Any fever? How about when putting pressure on her abdomen?","provider","comment","No fever, she says the gas feeling comes and goes.  Putting pressure though she does feel discomfort.","caregiver","comment","For her last BM, does %s recall its consistency?  What have her meals been before and since then?","provider","comment","shoot, now that I've asked it to her, she did say it was pretty much diarrhea for her last one.  As for food, nothing out of the ordinary.  Nothing greasy.  She says the abdominal pain is now increasing when she presses down.","caregiver","comment","Thanks for the update.  It's been another day, and with the pain increasing, I think you need to bring her into the ER.  When you do go in, you might want to print this conversation out for the docs to know what we know here.","provider","comment"],
            ]