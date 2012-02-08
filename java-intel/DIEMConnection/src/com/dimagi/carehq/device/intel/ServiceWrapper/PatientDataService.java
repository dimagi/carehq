/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.dimagi.carehq.device.intel.ServiceWrapper;

import com.intel.healthcare.integration.importdata.ArrayOfImportResult;
import com.intel.healthcare.integration.importdata.ImportResult;
import com.intel.healthcare.integration.importdata.Result;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.ws.Holder;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatient;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.Patient;

/**
 *
 * @author dmyung
 */
public class PatientDataService {

    private SecurityService _securitySvc;

    public PatientDataService(SecurityService svc) {
        this._securitySvc = svc;
    }

    public boolean UpdatePatient(Patient pt) {
		//Update or Create a patient
		//If InternalUserID matches, then existing record will update
		//If InternalUserID is empty and ExteranlUserID matches, then it'll update
		

        ArrayOfPatient patientArr = new ArrayOfPatient();
        patientArr.getPatient().add(pt);
        
        Holder<Result> importPatientsResult = new Holder<Result>();
        Holder<ArrayOfImportResult> importResults = new Holder<ArrayOfImportResult>();
        try {
            callImportPatients(patientArr, this._securitySvc.getSessionToken(), importPatientsResult, importResults);
        } catch (Exception ex) {
            Logger.getLogger(PatientDataService.class.getName()).log(Level.SEVERE, null, ex);
        }
        System.out.println("ImportPatientsResult: " + importPatientsResult.value);

        List<ImportResult> res = importResults.value.getImportResult();
        Iterator<ImportResult> itr = res.iterator();
        while (itr.hasNext()) {
            ImportResult ires = itr.next();

            System.out.println("\tImport: " + ires.getInternalIdentifier() + " Result: " + ires.getResult());
        }

        System.out.println("ImportPatientsResult: " + importPatientsResult.value);
        return true;
    }

    private void callImportPatients(org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfPatient demographics, java.lang.String secureSessionToken, javax.xml.ws.Holder<com.intel.healthcare.integration.importdata.Result> importPatientsResult, javax.xml.ws.Holder<com.intel.healthcare.integration.importdata.ArrayOfImportResult> importResults) {
        com.intel.healthcare.integration.importdata.ImportDataService service = new com.intel.healthcare.integration.importdata.ImportDataService();
        com.intel.healthcare.integration.importdata.IImportData port = service.getBasicHttpBindingIImportData();
        port.importPatients(demographics, secureSessionToken, importPatientsResult, importResults);
    }

   




}
