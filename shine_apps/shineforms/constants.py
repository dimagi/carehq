STR_MEPI_OUTCOME_FORM = 'http://shine.commcarehq.org/questionnaire/outcome'
STR_MEPI_FOLLOWUP_FORM = 'http://shine.commcarehq.org/questionnaire/followup'
STR_MEPI_LAB_FOUR_FORM = 'http://shine.commcarehq.org/lab/four'
STR_MEPI_LAB_THREE_FORM = 'http://shine.commcarehq.org/lab/three'
STR_MEPI_LAB_TWO_FORM = 'http://shine.commcarehq.org/lab/two'
STR_MEPI_LAB_ONE_FORM = 'http://shine.commcarehq.org/lab/one'
STR_MEPI_LABDATA_FORM = 'http://shine.commcarehq.org/questionnaire/labdata'
STR_MEPI_CLINICAL_QUEST_FORM = 'http://shine.commcarehq.org/questionnaire/clinical'
STR_MEPI_ENROLLMENT_FORM = 'http://shine.commcarehq.org/patient/reg'



xmlns_sequence = [
    STR_MEPI_ENROLLMENT_FORM,
    STR_MEPI_CLINICAL_QUEST_FORM,
    STR_MEPI_LABDATA_FORM,
    STR_MEPI_LAB_ONE_FORM,
    STR_MEPI_LAB_TWO_FORM,
    STR_MEPI_LAB_THREE_FORM,
    STR_MEPI_LAB_FOUR_FORM,
    STR_MEPI_FOLLOWUP_FORM,
    STR_MEPI_OUTCOME_FORM,
]

form_sequence = [
    'Enrollment',
    'Clinical Info',
    'Follow Up',
    'Lab Data',
    'Emergency Lab',
    'Biochemical Lab',
    'Speciation',
    'Sensitivity',
    'Outcome',
    ]

xmlns_display_map = {
   STR_MEPI_ENROLLMENT_FORM: "Enrollment",
   STR_MEPI_CLINICAL_QUEST_FORM: "Clinical Info",
   STR_MEPI_FOLLOWUP_FORM: "Old Follow Up/Outcome",
   STR_MEPI_LABDATA_FORM: "Lab Data",
   STR_MEPI_LAB_ONE_FORM: "Emergency Lab",
   STR_MEPI_LAB_TWO_FORM: "Biochemical Lab",
   STR_MEPI_LAB_THREE_FORM: "Speciation",
   STR_MEPI_LAB_FOUR_FORM: "Sensitivity",
   STR_MEPI_OUTCOME_FORM: "Outcome",
}
