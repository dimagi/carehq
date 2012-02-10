/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.dimagi.carehq.device.intel.ServiceWrapper;

import com.careinnovations.healthcare.integration.importdata.ArrayOfImportResult;
import com.careinnovations.healthcare.integration.importdata.ArrayOfInputValidationError;
import com.careinnovations.healthcare.integration.importdata.IImportData;
import com.careinnovations.healthcare.integration.importdata.ImportDataService;
import com.careinnovations.healthcare.integration.importdata.ImportResult;
import com.careinnovations.healthcare.integration.importdata.InputValidationError;
import com.careinnovations.healthcare.integration.importdata.Result;
import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.ws.Holder;
import org.datacontract.schemas._2004._07.careinnovations_healthcare_integration.ArrayOfPatient;
import org.datacontract.schemas._2004._07.careinnovations_healthcare_integration.Patient;
import org.json.JSONObject;

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
//			Logger.getLogger(PatientDataService.class.getName()).log(Level.SEVERE, null, ex);
			System.out.println("Exception updating the freaking patient: " + ex);
			return false;
		}

		List<ImportResult> res = importResults.value.getImportResult();
		Iterator<ImportResult> itr = res.iterator();
		while (itr.hasNext()) {
			ImportResult ires = itr.next();

			System.out.println("\tImport: " + ires.getInternalIdentifier() + " Result: " + ires.getResult());
			ArrayOfInputValidationError errors = ires.getErrors();
			List<InputValidationError> errors_list = errors.getInputValidationError();
			Iterator<InputValidationError> eres = errors_list.iterator();
			while(eres.hasNext()) {
				InputValidationError actual_error = eres.next();
				System.out.println("\t\tError: " + actual_error.getPropertyName() + ": " + actual_error.getErrorMessage() + " :: " + actual_error.getPropertyValue());
			}
		}

		System.out.println("ImportPatientsResult: " + importPatientsResult.value);
		return true;
	}

	private void callImportPatients(ArrayOfPatient demographics, java.lang.String secureSessionToken, javax.xml.ws.Holder<Result> importPatientsResult, javax.xml.ws.Holder<ArrayOfImportResult> importResults) {
		ImportDataService service = new ImportDataService();
		IImportData port = service.getBasicHttpBindingIImportData();
		port.importPatients(demographics, secureSessionToken, importPatientsResult, importResults);
	}
}
