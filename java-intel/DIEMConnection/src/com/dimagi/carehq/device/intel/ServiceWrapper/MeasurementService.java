/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.dimagi.carehq.device.intel.ServiceWrapper;

import java.util.Date;

/**
 *
 * @author dmyung
 */
public class MeasurementService {

    private SecurityService _securitySvc;

    public MeasurementService(SecurityService svc) {
        this._securitySvc = svc;
    }


}
