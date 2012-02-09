/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package patientdatahelper;

import com.dimagi.carehq.device.intel.ServiceWrapper.PatientDataService;
import com.dimagi.carehq.device.intel.ServiceWrapper.SecurityService;
import java.io.BufferedInputStream;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.datacontract.schemas._2004._07.careinnovations_healthcare_integration.Patient;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/**
 *
 * @author dmyung
 */
public class PatientDataHelper {
	/**
	 * @param args the command line arguments
	 */
	public static void main(String[] args) {
		// TODO code application logic here
		//patient_filename.json
		
		if (args.length == 0) {
			System.err.print("Error, you must specify some arguments");
			System.exit(0);
		}
		
		String file_path = "";
		if (args.length == 1) {
			file_path = args[0];
		}
		
		SecurityService secSvc = new SecurityService();
		try {
			System.setProperty("javax.net.ssl.trustStore", "jssecacerts");
			System.setProperty("javax.net.ssl.trustStorePassword", "changeit");
			System.setProperty("javax.net.ssl.keyStore", "client.ks");
			System.setProperty("javax.net.ssl.keyStorePassword", "dimagi4life");
			secSvc.Login("Admin", "!60RSr2QrX3!");

			try {
				System.out.println("Logged in: " + secSvc.isLoggedIn() + " Session: " + secSvc.getSessionToken());
			} catch (Exception ex) {
				Logger.getLogger(PatientDataHelper.class.getName()).log(Level.SEVERE, null, ex);
			}
		} catch (Exception e) {
			System.out.println("Security Login Error: " + e.getMessage());
			System.out.println("Security Login Stack: " + e.getStackTrace().toString());
		}
		secSvc.Logout();
	}


	private String loadPatientDataFile(String path) {
		byte[] buffer = new byte[(int)new File(path).length()];
		BufferedInputStream f = null;
		try {
			f = new BufferedInputStream(new FileInputStream(path));
			f.read(buffer);
		} catch (FileNotFoundException ex) {
		
		} catch (IOException iox) {

		}
		
		finally {
			if (f != null) {
				try {
					f.close();
				} catch (IOException ignored) {
				}
			}
		}
		return new String(buffer);
	}

	private ArrayList<Patient> loadPatientsFromJSON(String filepath) throws org.json.JSONException  {
		String patients_json = this.loadPatientDataFile(filepath);
		ArrayList<Patient> ret = new ArrayList<Patient>();
		try {
			JSONArray patients_array = new JSONArray(patients_json);

			int arrlength = patients_array.length();
			for (int i = 0; i < arrlength; i++) {
				try {
					JSONObject pt_json = patients_array.getJSONObject(i);
					Patient pt = this.makePatient(pt_json);
					ret.add(pt);
					
				} catch (JSONException e) {
				}
			}
		} catch (JSONException e) {
		}
		return ret;
	}


	public Patient makePatient(JSONObject ptJSON) throws org.json.JSONException {
		Patient ret = new Patient();
		ret.setDataSource("Intel Health Guide System");
		ret.setExternalUserID(ptJSON.getString("ExternalUserID"));
		ret.setInternalUserID(ptJSON.getString("InternalUserID"));
		ret.setFirstName(ptJSON.getString("FirstName"));
		ret.setLastName(ptJSON.getString("LastName"));
		ret.setGender(ptJSON.getString("Gender"));
		ret.setTimeZone("Eastern Standard Time");
		ret.setTimeZoneID((short)30);
		ret.setStatusID((short)1);
		ret.setAddress1(ptJSON.getString("Address1"));
		ret.setCity(ptJSON.getString("City"));
		ret.setState(ptJSON.getString("State"));
		ret.setPostalCode(ptJSON.getString("PostalCode"));
		ret.setCountry("USA");
		ret.setPhoneNumber(ptJSON.getString("PhoneNumber"));
		ret.setPinEntryRequired(false);
		ret.setCultureID((short)1033);
		System.out.println("Made patient from json: " + ret.getInternalUserID());
		return ret;
	}
	
	public void ImportOrUpdateFromFile(SecurityService secSvc, String file_path) throws org.json.JSONException {
		PatientDataService isvc = new PatientDataService(secSvc);
		ArrayList<Patient> patients = this.loadPatientsFromJSON(file_path);
		Iterator<Patient> pt_it = patients.iterator();
		while (pt_it.hasNext()) {
			Patient pt = pt_it.next();
			System.out.println("Updating Patient " + pt.toString());
			isvc.UpdatePatient(pt);
			System.out.println("Patient update complete");
		}
	}
	
}
