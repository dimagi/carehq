/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package diemapp;

import com.dimagi.carehq.device.intel.ServiceWrapper.AdherenceService;
import com.dimagi.carehq.device.intel.ServiceWrapper.PatientDataService;
import com.dimagi.carehq.device.intel.ServiceWrapper.SecurityService;
import com.dimagi.carehq.device.intel.ServiceWrapper.SessionService;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.AdherenceDetail;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.AdherenceSummary;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.Measurement;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.Patient;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.PatientSession;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ProtocolPerformed;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.Threshold;

/**
 *
 * @author dmyung
 */
public class Main {
	/**
	 * @param args the command line arguments
	 */
	public static void main(String[] args) {
		// TODO code application logic here

		if (args.length == 0) {
			System.err.print("Error, you must specify some arguments");
			System.exit(0);
		}

		String run_mode = "";
		if (args.length == 1) {
			
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
				Logger.getLogger(Main.class.getName()).log(Level.SEVERE, null, ex);
			}
		} catch (Exception e) {
			System.out.println("Error: " + e.getMessage());
			System.out.println("Stack: " + e.getStackTrace().toString());
		}
		secSvc.Logout();
	}

	public void Ping(SecurityService secSvc) {
		System.out.println(secSvc.Ping(3));
	}

	public void SessionChecker(SecurityService secSvc) {

		SessionService sessSvc = new SessionService(secSvc);
		System.out.println("Got session");
		Patient ptzero = sessSvc.GetPatient(SessionService.DimagiZeroID);


		List<String> sessions = sessSvc.getSessionIDsForPatient(SessionService.DimagiZeroID);

		System.out.println("Sessions for Zero: " + sessions.size());

		Iterator<String> it = sessions.iterator();
		while (it.hasNext()) {
			String sess_id = it.next();
			PatientSession ptSess = sessSvc.getSinglePatientSession(sess_id);
			String beginTime = ptSess.getSubmittedTime().toString();
			System.out.println("\n***********************\nSession ID: " + sess_id + " Time: " + beginTime);


			List<Measurement> measurements = ptSess.getMeasurements().getMeasurement();
			List<Threshold> thresholds = ptSess.getPatientThresholds().getThreshold();
			List<ProtocolPerformed> protocols = ptSess.getProtocolsPerformed().getProtocolPerformed();
			String submit_time = ptSess.getSubmittedTime().toString();

			//System.out.println("Session: " + sess_id + " Begin: " + beginTime + " - submitted: " + submit_time);

			System.out.println("\t**** Protocols Run:");
			Iterator<ProtocolPerformed> proto = protocols.iterator();
			while (proto.hasNext()) {
				ProtocolPerformed protoperf = proto.next();
				System.out.println("\t\t" + protoperf.getDescription());
			}

			System.out.println("\t**** Thresholds:");
			Iterator<Threshold> thrs = thresholds.iterator();
			while (thrs.hasNext()) {
				Threshold threshold = thrs.next();
				//-1 == Lesser
				//1 = equal
				//1 = greater
				//if -1 the submited time os BEFORE the threshold was made
				//if 1 the submitted time was AFTER the threshold was made

				boolean doesApply = false;
				if (ptSess.getSubmittedTime().compare(threshold.getDateModified()) < 0) {
					doesApply = false;
				} else {
					doesApply = true;
				}
				System.out.println("\t\t" + threshold.getMeasurementFieldTypeName() + " High: " + threshold.getHigh() + threshold.getUnits() + " Low: " + threshold.getLow() + threshold.getUnits() + " Applies : " + doesApply + " Timestamp: " + threshold.getDateModified());
			}

			System.out.println("\t**** Measurements:");
			Iterator<Measurement> mi = measurements.iterator();
			while (mi.hasNext()) {
				Measurement meas = mi.next();
				System.out.println("\n\t\t" + meas.getMeasurementFieldTypeName() + " Value: " + meas.getValue() + " " + meas.getUnits() + " Manual: " + meas.isIsManualEntry());
				System.out.println("\t\tThreshold: " + meas.getThresholdLow() + " - " + meas.getThresholdHigh() + " Violation: " + meas.isIsThresholdViolation());
			}

//            
		}
	}

	public void AdherenceChecher(SecurityService secSvc) {
		AdherenceService ads = new AdherenceService(secSvc);


		//AdherenceDetails
		System.out.println("\n#################################\nAdherence Details\n");
		ArrayList<AdherenceDetail> details = ads.getAdherenceDetails(SessionService.DimagiZeroID);

		Iterator<AdherenceDetail> it3 = details.iterator();
		String session_id = "";
		String protocol = "";
		while (it3.hasNext()) {
			AdherenceDetail ad = it3.next();
			String sess = ad.getSessionID();
			if (!sess.equals(session_id)) {
				System.out.println("\t****Session: " + sess);
				session_id = sess;
			}
			String proto = ad.getCarePlanProtocol();
			if (!protocol.equals(proto)) {
				protocol = proto;
				System.out.println("\t\tProtocol: " + proto);
			}
			if (ad.getTaskTypeID() == 4) {
				System.out.println("\n\t\tTask: " + ad.getCarePlanTask() + "\n\t\tAnswer: " + ad.getAnswer() + ", violation: " + ad.isThresholdViolation());
			}
		}


		System.out.println("\n$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\nAdherence Summary\n");
		List<AdherenceSummary> summaries = ads.getAdherenceSummary(SessionService.DimagiZeroID);
		Iterator<AdherenceSummary> it4 = summaries.iterator();
		while (it4.hasNext()) {
			AdherenceSummary sum = it4.next();
			System.out.println("\t\tSummary: " + sum.getCarePlanID() + " Session: " + sum.getSessionID() + " Is Extra: " + sum.isExtraSession() + " Status: " + sum.getStatus() + " Measurement: " + sum.getMeasurementID());
			System.out.println("\t\t\tDate Scheduled: " + sum.getDateScheduled());
			System.out.println("\t\t\tDate Performed: " + sum.getDatePerformed());
			System.out.println("\t\t\tDate Submitted: " + sum.getDateSubmitted());
		}

	}

	public void Importer(SecurityService secSvc) {
		String addr = UUID.randomUUID().toString();
		System.out.println("Original address: " + ptzero.getAddress1());
		System.out.println("Set addr to: " + addr);
		
		ptzero.setAddress1(addr);
		PatientDataService isvc = new PatientDataService(secSvc);
		isvc.UpdatePatient(ptzero);
		
		System.out.println("Update complete");
		secSvc.Logout();
		System.out.println("Logging in again");
		secSvc.Login("Admin", "!60RSr2QrX3!");
		
		System.out.println("Reloading patient");
		Patient ptzero_refresh = sessSvc.GetPatient(SessionService.DimagiZeroID);
		System.out.println("Patient reloaded");
		System.out.println("Reloaded Patient:");
		System.out.println("1: " + ptzero_refresh.getAddress1());
		System.out.println("2: " + addr);
	}

	public void CCDChecker(SecurityService secSvc) {
		SessionService sessSvc = new SessionService(secSvc);
		System.out.println("Got session");
		Patient ptzero = sessSvc.GetPatient(SessionService.DimagiZeroID);

		String hl7str = sessSvc.getHl7Session(sess_id);
//
//            try{
//                // Create file
//                FileWriter fstream = new FileWriter(sess_id + "_hl7.xml");
//                BufferedWriter out = new BufferedWriter(fstream);
//                out.write(hl7str);
//                //Close the output stream
//                out.close();
//            } catch (Exception e) {//Catch exception if any
//                System.err.println("Error: " + e.getMessage());
//            }

	}
}
