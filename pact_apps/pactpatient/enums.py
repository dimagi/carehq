
GENDER_CHOICES = (
       ('m','Male'),
       ('f','Female'),
       ('u','Undefined'),
   )



REGIMEN_CHOICES = (
    ('None', '-- No Regimen --'),
    ('QD', 'QD - Once a day'),
    ('BID', 'BID - Twice a day'),
    ('QD-AM', 'QD - Once a day (Morning)'),
    ('QD-PM', 'QD - Once a day (Evening)'),
    ('TID', 'TID - Three times a day'),
    ('QID', 'QID - Four times a day'),
    )

PACT_ARM_CHOICES = (
    ('HP', [('HP', 'HP - Health Promoter'),

    ('HP1', 'Health Promoter 1 (HP-1)'),
    ('HP2', 'Health Promoter 2 (HP-2)'),
    ('HP3', 'Health Promoter 3 (HP-3)')]),

    ('DOT', [('DOT', 'DOT - Directly Observed Therapy'),
    ('DOT7', 'Directly Observed Therapy 7 (DOT-7)'),
    ('DOT5', 'Directly Observed Therapy 5 (DOT-5)'),
    ('DOT3', 'Directly Observed Therapy 3 (DOT-3)'),
    ('DOT1', 'Directly Observed Therapy 1 (DOT-1)')]),

    ('Discharged', 'Discharged'),
    ('', '')
    #todo: more choices
    )

PACT_RACE_CHOICES = (
    ('white', 'White'),
    ('black-or-africanamerican', 'Black or African American'),
    ('asian', 'Asian'),
    ('american-indian-alaska-native', 'American Indian/Alaska Native'),
    ('more-than-one', 'More than one race'),
    ('unknown', 'Unknown or not reported'),
)

PACT_LANGUAGE_CHOICES = (
    ('english', 'English'),
    ('spanish', 'Spanish'),
    ('haitian_creole', 'Haitian Creole'),
    ('portugese', 'Portugese'),
)
PACT_HIV_CLINIC_CHOICES = (
    ("brigham_and_womens_hospital","Brigham and Women's Hospital"),
    ("massachusetts_general_hospital","Massachusetts General Hospital"),
    ("massachusetts_general_hospital_chelsea","Massachusetts General Hospital - Chelsea"),
    ("massachusetts_general_hospital_charlestown","Massachusetts General Hospital - Charlestown"),
    ("boston_healthcare_for_the_homeless_program","Boston Healthcare for the Homeless Program"),
    ("beth_israel_deaconess_medical_center","Beth Israel Deaconess Medical Center"),
    ("cambridge_health_alliance","Cambridge Health Alliance"),
    ("cambridge_health_alliance_somerville","Cambridge Health Alliance - Somerville"),
    ("cambridge_health_alliancewindsor_st","Cambridge Health Alliance-Windsor St"),
    ("codman_square_health_center","Codman Square Health Center"),
    ("dimock_center","Dimock Center"),
    ("dorchester_house_multiservice_center","Dorchester House Multi-Service Center"),
    ("east_boston_neighborhood_health_clinic","East Boston Neighborhood Health Clinic"),
    ("faulkner_hospital","Faulkner Hospital"),
    ("fenway_health_clinic","Fenway Health Clinic"),
    ("harvard_vanguard_medical_associates","Harvard Vanguard Medical Associates"),
    ("martha_eliot_health_center","Martha Eliot Health Center"),
    ("tufts_medical_center","Tufts Medical Center"),
    ("neponset_health_center","Neponset Health Center"),
    ("lemuel_shattuck_hospital","Lemuel Shattuck Hospital"),
    ("st_elizabeths_medical_center","St. Elizabeth's Medical Center"),
    ("uphams_corner_health_center","Upham's Corner Health Center"),
    ("boston_medical_center","Boston Medical Center"),

)