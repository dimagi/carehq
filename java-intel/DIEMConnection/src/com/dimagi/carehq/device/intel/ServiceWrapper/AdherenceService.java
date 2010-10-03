/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.dimagi.carehq.device.intel.ServiceWrapper;

import com.intel.healthcare.integration.extracts.ExtractResult;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.ws.Holder;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.AdherenceDetail;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.AdherenceDetailFilter;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.AdherenceDetailFilterCondition;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.AdherenceSummaryFilter;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.AdherenceSummaryFilterCondition;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfAdherenceDetail;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfAdherenceDetailFilterCondition;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfAdherenceSummary;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.AdherenceSummary;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfAdherenceSummaryFilterCondition;
import org.datacontract.schemas._2004._07.intel_healthcare_integration.FilterOperator;

/**
 *
 * @author dmyung
 */
public class AdherenceService {
    private SecurityService _securitySvc;

    public AdherenceService(SecurityService svc) {
        this._securitySvc = svc;
    }


    public ArrayList<AdherenceDetail> getAdherenceDetails(String ptInternalID) {
        ArrayOfAdherenceDetailFilterCondition adherehenceFilterConditions = new ArrayOfAdherenceDetailFilterCondition();
        AdherenceDetailFilterCondition cond = new AdherenceDetailFilterCondition();

        cond.setLValue(AdherenceDetailFilter.PATIENT_INTERNAL_ID);
        cond.setOperator(FilterOperator.EQUALS);
        cond.setRValue(ptInternalID);

        adherehenceFilterConditions.getAdherenceDetailFilterCondition().add(cond);

        Holder<ExtractResult> getAdherenceDetailsResult = new Holder<ExtractResult>();
        Holder<ArrayOfAdherenceDetail> adherenceExtractData = new Holder<ArrayOfAdherenceDetail>();

        boolean doContinue = false;
        ArrayList<AdherenceDetail> all_sessions = new ArrayList<AdherenceDetail>();
        while(true) {
            try {
                callGetAdherenceDetails(this._securitySvc.getSessionToken(), doContinue, adherehenceFilterConditions, getAdherenceDetailsResult, adherenceExtractData);
            } catch (Exception ex) {
                Logger.getLogger(AdherenceService.class.getName()).log(Level.SEVERE, null, ex);
            }
            
            List<AdherenceDetail> details = adherenceExtractData.value.getAdherenceDetail();
            Iterator<AdherenceDetail> it = details.iterator();
            while(it.hasNext()) {
                AdherenceDetail pt = it.next();
                all_sessions.add(pt);
            }

            if (getAdherenceDetailsResult.value.equals(ExtractResult.IN_PROGRESS)) {
                doContinue = true;
                continue;
            } else {
                break;
            }
        }
        return all_sessions;
    }

    public List<AdherenceSummary> getAdherenceSummary(String ptInternalID) {
        ArrayOfAdherenceSummaryFilterCondition filterConditions = new ArrayOfAdherenceSummaryFilterCondition();
        AdherenceSummaryFilterCondition cond = new AdherenceSummaryFilterCondition();

        //see page 21 of programmer's reference for date filters
        cond.setLValue(AdherenceSummaryFilter.PATIENT_INTERNAL_ID);
        cond.setOperator(FilterOperator.EQUALS);
        cond.setRValue(ptInternalID);

        filterConditions.getAdherenceSummaryFilterCondition().add(cond);
        Holder<ExtractResult> getAdherenceSummariesResult = new Holder<ExtractResult>();
        Holder<ArrayOfAdherenceSummary> extractData = new Holder<ArrayOfAdherenceSummary>();

        try {
            callGetAdherenceSummaries(this._securitySvc.getSessionToken(), false, filterConditions, getAdherenceSummariesResult, extractData);
        } catch (Exception ex) {
            Logger.getLogger(AdherenceService.class.getName()).log(Level.SEVERE, null, ex);
        }

        return extractData.value.getAdherenceSummary();
    }


    private void callGetAdherenceDetails(java.lang.String secureSessionToken, java.lang.Boolean continueExtract, org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfAdherenceDetailFilterCondition filterConditions, javax.xml.ws.Holder<com.intel.healthcare.integration.extracts.ExtractResult> getAdherenceDetailsResult, javax.xml.ws.Holder<org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfAdherenceDetail> extractData) {
        com.intel.healthcare.integration.extracts.ExtractDataService service = new com.intel.healthcare.integration.extracts.ExtractDataService();
        com.intel.healthcare.integration.extracts.IExtractData port = service.getBasicHttpBindingIExtractData();
        port.getAdherenceDetails(secureSessionToken, continueExtract, filterConditions, getAdherenceDetailsResult, extractData);
    }

    private void callGetAdherenceSummaries(java.lang.String secureSessionToken, java.lang.Boolean continueExtract, org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfAdherenceSummaryFilterCondition filterConditions, javax.xml.ws.Holder<com.intel.healthcare.integration.extracts.ExtractResult> getAdherenceSummariesResult, javax.xml.ws.Holder<org.datacontract.schemas._2004._07.intel_healthcare_integration.ArrayOfAdherenceSummary> extractData) {
        com.intel.healthcare.integration.extracts.ExtractDataService service = new com.intel.healthcare.integration.extracts.ExtractDataService();
        com.intel.healthcare.integration.extracts.IExtractData port = service.getBasicHttpBindingIExtractData();
        port.getAdherenceSummaries(secureSessionToken, continueExtract, filterConditions, getAdherenceSummariesResult, extractData);
    }

    private static Boolean ping() {
        com.intel.healthcare.integration.authenticate.AuthenticateService service = new com.intel.healthcare.integration.authenticate.AuthenticateService();
        com.intel.healthcare.integration.authenticate.IAuthenticate port = service.getBasicHttpBindingIAuthenticate();
        return port.ping();
    }



}
