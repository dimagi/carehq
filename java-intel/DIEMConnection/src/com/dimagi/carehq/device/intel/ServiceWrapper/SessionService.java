/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.dimagi.carehq.device.intel.ServiceWrapper;

import com.intel.healthcare.integration.extracts.ExtractResult;
import com.microsoft.schemas._2003._10.serialization.arrays.ArrayOfstring;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.Vector;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.ws.Holder;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatient;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatientFilterCondition;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatientSession;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatientSessionFilterCondition;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.FilterOperator;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.Measurement;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.Patient;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.PatientFilter;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.PatientFilterCondition;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.PatientSession;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.PatientSessionFilter;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.PatientSessionFilterCondition;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ProtocolPerformed;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.Threshold;

/**
 *
 * @author dmyung
 */
public class SessionService {
    //public static String DimagiZeroID = "F5942BFF-4692-4000-BCC2-A1465208E426";
    public static String DimagiZeroID = "74D7AF9D-56F5-4BA2-BC9D-B4D17020BE28";

    
    private SecurityService _securitySvc;

    public SessionService(SecurityService svc) {
        this._securitySvc = svc;
    }    

    public Patient GetPatient(String ptInternalID) {
        try {
            return callGetPatientByInternalID(this._securitySvc.getSessionToken(), ptInternalID);
        } catch (Exception ex) {
            Logger.getLogger(SessionService.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }

    public ArrayList<Patient> GetAllPatients() {
        ArrayOfPatientFilterCondition filterConditions = new ArrayOfPatientFilterCondition();
        Holder<ExtractResult> getPatientsResult = new Holder<ExtractResult>();
        Holder<ArrayOfPatient> extractData = new Holder<ArrayOfPatient>();

//        PatientFilterCondition cond = new PatientFilterCondition();
 //       cond.setLValue(PatientFilter.INTERNAL_USER_ID);
  //      cond.setOperator(FilterOperator.EQUALS);
   //     cond.setRValue(ptInternalID);


        ArrayList<Patient> all_patients = new ArrayList<Patient>();
        boolean doContinue = false;
        while(true) {
            try {
                callGetPatients(this._securitySvc.getSessionToken(), doContinue, filterConditions, getPatientsResult, extractData);
            } catch (Exception ex) {
                Logger.getLogger(SessionService.class.getName()).log(Level.SEVERE, null, ex);
            }
            System.out.println(getPatientsResult.value);
            List<Patient> pts = extractData.value.getPatient();
            Iterator<Patient> it = pts.iterator();
            while(it.hasNext()) {
                Patient pt = it.next();
                all_patients.add(pt);
                String ptid = pt.getInternalUserID();
                System.out.println("Pt ID: " + ptid + " :: " + pt.getFirstName() + " " + pt.getLastName());                
            }
            if (getPatientsResult.value.equals(com.intel.healthcare.integration.extracts.ExtractResult.IN_PROGRESS)) {
                doContinue = true;
                continue;
            } else {
                break;
            }
        } 
        return all_patients;
    }


    public String getHl7Session(String session_id) {
        Holder<ExtractResult> getStandardFormatPatientSessionResult = new Holder<ExtractResult>();
        Holder<String> patientSession = new Holder<String>();
        try {
            this.callGetStandardFormatPatientSession(this._securitySvc.getSessionToken(), session_id, false, "HL7V3CCD", getStandardFormatPatientSessionResult, patientSession);
        } catch (Exception ex) {
            Logger.getLogger(SessionService.class.getName()).log(Level.SEVERE, null, ex);
        }
        //System.out.println("Session data hl7: " + patientSession.value);
        return patientSession.value;
    }


    public PatientSession getSinglePatientSession(String patientSessionID) {
        Holder<ExtractResult> getPatientSessionResult = new Holder<ExtractResult>();
        Holder<PatientSession> patientSession = new Holder<PatientSession>();
        try {
            callGetPatientSession(this._securitySvc.getSessionToken(), patientSessionID, false, getPatientSessionResult, patientSession);
        } catch (Exception ex) {
            Logger.getLogger(SessionService.class.getName()).log(Level.SEVERE, null, ex);
            System.out.println("WTF: " + ex.getMessage());
        }
        //todo: put a check on the extractResult
        return patientSession.value;
    }



    
    /*
     * Massive call to get ALL the session information for ALL patients (intel format).
     */
    public List<PatientSession> getAllPatientSessions() {
        Holder<ExtractResult> getPatientSessionsResult = new Holder<ExtractResult>();
        Holder<ArrayOfPatientSession> extractData = new Holder<ArrayOfPatientSession>();
        try {
            callGetPatientSessions(this._securitySvc.getSessionToken(), false, false, false, getPatientSessionsResult, extractData);
        } catch (Exception ex) {
            Logger.getLogger(SessionService.class.getName()).log(Level.SEVERE, null, ex);
        }
        List<PatientSession> sessions  = extractData.value.getPatientSession();

        Iterator<PatientSession> it = sessions.iterator();
        while(it.hasNext()) {
            PatientSession sess = it.next();
            String sess_id = sess.getSessionID();
            String beginTime = sess.getBeginTime().toString();
            List<Measurement> measurements = sess.getMeasurements().getMeasurement();
            List<Threshold> thresholds = sess.getPatientThresholds().getThreshold();
            List<ProtocolPerformed> protocols = sess.getProtocolsPerformed().getProtocolPerformed();
            String submit_time = sess.getSubmittedTime().toString();

            System.out.println("Session: " + sess_id + " Begin: " + beginTime + " - submitted: " + submit_time);

            System.out.println("Protocols:");
            Iterator<ProtocolPerformed> proto = protocols.iterator();
            while(proto.hasNext()) {
                ProtocolPerformed protoperf = proto.next();
                System.out.println("\t" + protoperf.getDescription());
            }

            System.out.println("Thresholds:");
            Iterator<Threshold> thrs = thresholds.iterator();
            while(proto.hasNext()) {
                Threshold threshold = thrs.next();
                System.out.println("\t" + threshold.getMeasurementFieldTypeName() + " High: " + threshold.getHigh() + threshold.getUnits() + " Low: " + threshold.getLow() + threshold.getUnits() + " Date: " + threshold.getDateModified().toString());
            }

            System.out.println("Measurements:");
            Iterator<Measurement> mi = measurements.iterator();
            while(mi.hasNext()) {
                Measurement meas = mi.next();
                System.out.println("\t" + meas.getMeasurementFieldTypeName() + " Value: " + meas.getValue() + " " + meas.getUnits() + " Threshold: " + meas.isIsThresholdViolation());
            }
        }

        return sessions;
    }

    public List<String> getSessionIDsForPatient(String ptid) {
        //establish filter conditions
        ArrayOfPatientSessionFilterCondition ptFilterConditions = new ArrayOfPatientSessionFilterCondition();

        PatientSessionFilterCondition ptf = new PatientSessionFilterCondition();
        ptf.setLValue(PatientSessionFilter.PATIENT_INTERNAL_ID);
        ptf.setRValue(ptid);
        ptf.setOperator(FilterOperator.EQUALS);
        ptFilterConditions.getPatientSessionFilterCondition().add(ptf);        
        
        PatientSessionFilterCondition time_start = new PatientSessionFilterCondition();
        time_start.setLValue(PatientSessionFilter.DATE_SUBMITTED);
        time_start.setRValue("2010-08-01 06:00:00.000");    //YYYY-MM-DD HH:MM:SS:MMM
        time_start.setOperator(FilterOperator.GREATER_THAN);
        //ptFilterConditions.getPatientSessionFilterCondition().add(time_start);

        PatientSessionFilterCondition time_end = new PatientSessionFilterCondition();
        time_end.setLValue(PatientSessionFilter.DATE_SUBMITTED);
        time_end.setRValue("2010-08-01 23:59:00.000");
        time_end.setOperator(FilterOperator.LESS_THAN);
        //ptFilterConditions.getPatientSessionFilterCondition().add(time_end);

        //prepare the extract results
        Holder<ExtractResult> getPatientSessionIDsResult = new Holder<ExtractResult>();
        //actual extract result data
        Holder<ArrayOfstring> sessionIDExtractData = new Holder<ArrayOfstring>();
        try {
            callGetPatientSessionIDs(this._securitySvc.getSessionToken(), false, false, ptFilterConditions, getPatientSessionIDsResult, sessionIDExtractData);
        } catch (Exception ex) {
            Logger.getLogger(SessionService.class.getName()).log(Level.SEVERE, null, ex);
        }
        String extract_val = getPatientSessionIDsResult.value.value();
            System.out.println("GetSessionIDs result: " + extract_val);
        if (extract_val.equals("ExtractFilterError")) {
            return null;
        }
        List<String> sessionids = sessionIDExtractData.value.getString();
        return sessionids;
    }


    /*
     * Private calls to Intel services directly.
     * These are the direct calls to the web services and should be wrapped by public accessors.
     */

    //Intel design extract
    private void callGetPatientSessions(String secureSessionToken, Boolean continueExtract, Boolean markSent, Boolean unsentOnly, Holder<ExtractResult> getPatientSessionsResult, Holder<ArrayOfPatientSession> extractData) {
        com.intel.healthcare.integration.extracts.ExtractDataService service = new com.intel.healthcare.integration.extracts.ExtractDataService();
        com.intel.healthcare.integration.extracts.IExtractData port = service.getBasicHttpBindingIExtractData();
        port.getPatientSessions(secureSessionToken, continueExtract, markSent, unsentOnly, getPatientSessionsResult, extractData);
    }

    //Intel design extract
    private void callGetPatientSession(java.lang.String secureSessionToken, java.lang.String patientSessionID, java.lang.Boolean markSent, javax.xml.ws.Holder<com.intel.healthcare.integration.extracts.ExtractResult> getPatientSessionResult, javax.xml.ws.Holder<org.datacontract.schemas._2004._07.intel_healthcare_integration.PatientSession> patientSession) {
        com.intel.healthcare.integration.extracts.ExtractDataService service = new com.intel.healthcare.integration.extracts.ExtractDataService();
        com.intel.healthcare.integration.extracts.IExtractData port = service.getBasicHttpBindingIExtractData();
        port.getPatientSession(secureSessionToken, patientSessionID, markSent, getPatientSessionResult, patientSession);
    }

    private void callGetStandardFormatPatientSession(String secureSessionToken, String patientSessionID, Boolean markSent, String dataFormatType, Holder<ExtractResult> getStandardFormatPatientSessionResult, Holder<String> patientSession) {
        com.intel.healthcare.integration.extracts.ExtractDataService service = new com.intel.healthcare.integration.extracts.ExtractDataService();
        com.intel.healthcare.integration.extracts.IExtractData port = service.getBasicHttpBindingIExtractData();
        port.getStandardFormatPatientSession(secureSessionToken, patientSessionID, markSent, dataFormatType, getStandardFormatPatientSessionResult, patientSession);
    }


    

    private static void callGetPatientSessionIDs(java.lang.String secureSessionToken, java.lang.Boolean unsentOnly, java.lang.Boolean continueExtract, org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatientSessionFilterCondition filterConditions, javax.xml.ws.Holder<com.intel.healthcare.integration.extracts.ExtractResult> getPatientSessionIDsResult, javax.xml.ws.Holder<com.microsoft.schemas._2003._10.serialization.arrays.ArrayOfstring> extractData) {
        com.intel.healthcare.integration.extracts.ExtractDataService service = new com.intel.healthcare.integration.extracts.ExtractDataService();
        com.intel.healthcare.integration.extracts.IExtractData port = service.getBasicHttpBindingIExtractData();
        port.getPatientSessionIDs(secureSessionToken, unsentOnly, continueExtract, filterConditions, getPatientSessionIDsResult, extractData);
    }

    private void callGetPatients(java.lang.String secureSessionToken, java.lang.Boolean continueExtract, org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatientFilterCondition filterConditions, javax.xml.ws.Holder<com.intel.healthcare.integration.extracts.ExtractResult> getPatientsResult, javax.xml.ws.Holder<org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatient> extractData) {
        com.intel.healthcare.integration.extracts.ExtractDataService service = new com.intel.healthcare.integration.extracts.ExtractDataService();
        com.intel.healthcare.integration.extracts.IExtractData port = service.getBasicHttpBindingIExtractData();
        port.getPatients(secureSessionToken, continueExtract, filterConditions, getPatientsResult, extractData);
    }

    private static Patient callGetPatientByInternalID(java.lang.String secureSessionToken, java.lang.String internalID) {
        com.intel.healthcare.integration.userlookup.UserLookupService service = new com.intel.healthcare.integration.userlookup.UserLookupService();
        com.intel.healthcare.integration.userlookup.IUserLookup port = service.getBasicHttpBindingIUserLookup();
        return port.getPatientByInternalID(secureSessionToken, internalID);
    }
}
