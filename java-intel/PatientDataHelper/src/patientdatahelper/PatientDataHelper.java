/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package patientdatahelper;

import com.dimagi.carehq.device.intel.ServiceWrapper.PatientDataService;
import com.dimagi.carehq.device.intel.ServiceWrapper.SecurityService;
import com.dimagi.carehq.device.intel.ServiceWrapper.SessionService;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Calendar;
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

	private SecurityService _secSvc;
	
	public static void main(String[] args) {
		// TODO code application logic here
		//patient_filename.json
		
		//if (args.length == 0) {
		//System.err.print("Error, you must specify some arguments");
		//System.exit(0);
		//}
		//
		//String file_path = "";
		//if (args.length == 1) {
		//file_path = args[0];
		//}
		
		BufferedReader in = new BufferedReader(new InputStreamReader(System.in));
		StringBuilder sb = new StringBuilder();
		
		String s;
		try {
			while ((s = in.readLine()) != null && s.length() != 0) {
				sb.append(s);
				// An empty line or Ctrl-Z terminates the program
			}
		} catch (java.io.IOException ex) {
			
		}
				
		SecurityService secSvc = new SecurityService();
		try {
			System.setProperty("javax.net.ssl.trustStore", "/home/dmyung/workspaces/pycharm/ashand-project/carehq/java-intel/PatientDataHelper/dist/jssecacerts");
			System.setProperty("javax.net.ssl.trustStorePassword", "changeit");
			System.setProperty("javax.net.ssl.keyStore", "/home/dmyung/workspaces/pycharm/ashand-project/carehq/java-intel/PatientDataHelper/dist/client.ks");
			System.setProperty("javax.net.ssl.keyStorePassword", "dimagi4life");
			secSvc.Login("Admin", "bVFiUHbqRR_2");

			try {
				System.out.println("Logged in: " + secSvc.isLoggedIn() + " Session: " + secSvc.getSessionToken());

				SessionService sessSvc = new SessionService(secSvc);
				System.out.println("Got session");
				Patient ptzero = sessSvc.GetPatient("07AB02B4-F4AD-4BCA-BEBF-34E4A392DDD9");
				System.out.println("Got Patient: " + ptzero.getExternalUserID());
				ptzero.setAddress1("585 Massachusetts Avenue");
				ptzero.setAddress2("Suite 3");
//				ptzero.setPhoneNumber("(617) 649-2214");

				PatientDataService isvc = new PatientDataService(secSvc);
				isvc.UpdatePatient(ptzero);
				System.out.println("Updated patient zero");




				PatientDataHelper helper = new PatientDataHelper(secSvc);
				helper.ImportOrUpdateFromString(sb.toString());
			} catch (Exception ex) {
				Logger.getLogger(PatientDataHelper.class.getName()).log(Level.SEVERE, null, ex);
			}
		} 
		catch (Exception e) {
			System.out.println("Security Login Error: " + e.getMessage());
			System.out.println("Security Login Stack: " + e.getStackTrace().toString());
		} 
		finally {
			secSvc.Logout();
		}

	}

	public PatientDataHelper(SecurityService secSvc) {
		this._secSvc = secSvc;
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

	private ArrayList<Patient> loadPatientsFromJSON(String patients_json) throws org.json.JSONException  {
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
		System.out.println(ret.getExternalUserID());
		//ret.setExternalUserID2(ptJSON.getString("DocID")); //doc ID
		System.out.println(ret.getExternalUserID2());
//		ret.setInternalUserID(ptJSON.getString("InternalUserID"));
		ret.setInternalUserID(null);
		ret.setFirstName(ptJSON.getString("FirstName"));
		ret.setLastName(ptJSON.getString("LastName"));
		ret.setMiddleInitial("");

		Calendar birthdate = Calendar.getInstance();
		birthdate.set(1976, 7, 4);
		ret.setBirthDate(birthdate);
		
		ret.setGender(ptJSON.getString("Gender"));
		ret.setTimeZone("Eastern Standard Time");
		ret.setTimeZoneID((short)30);
		ret.setStatusID((short)1);
		ret.setAddress1("585 Massachusetts Avenue Suite 3");
		ret.setAddress2("");
		ret.setAddress3("");
		ret.setCity("Cambridge");
		ret.setState("MA");
		ret.setPostalCode("02139");
		ret.setCountry("USA");
		ret.setPhoneNumber("(617) 649-2214");
		ret.setEmail1("");
		ret.setEmail2("");
		ret.setEmail3("");
		
		ret.setHcmsUserName("");
		
		ret.setPinEntryRequired(false);
		ret.setPin("");
		ret.setCultureID((short)1033);
		System.out.println("Made patient from json: " + ret.getExternalUserID());
		return ret;
	}
	
	public void ImportOrUpdateFromString(String json_string) throws org.json.JSONException {
		PatientDataService isvc = new PatientDataService(this._secSvc);
		ArrayList<Patient> patients = this.loadPatientsFromJSON(json_string);
		Iterator<Patient> pt_it = patients.iterator();
		while (pt_it.hasNext()) {
			Patient pt = pt_it.next();
			System.out.println("Updating Patient " + pt.toString());
			isvc.UpdatePatient(pt);
			System.out.println("Patient update complete");
		}
	}
	
}
