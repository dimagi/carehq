/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package com.dimagi.carehq.device.intel.ServiceWrapper;

/**
 *
 * @author dmyung
 */
public class SecurityService {
    private static String NULL_SESSION = "00000000-0000-0000-0000-000000000000";

    private String _sessionToken = null;
    public String getSessionToken() throws Exception {

        if (this._isLoggedIn == false) {
            throw new Exception("Error, security service must be logged in");
        }
        return _sessionToken;
    }

    private boolean _isLoggedIn = false;
    public boolean isLoggedIn() {
        return _isLoggedIn;
    }

    public boolean Ping(int count) {
        boolean ret = false;        
        for (int i = 0; i < count; i++) {
            ret = this.callPing();
        }
        return ret;        
    }


    public boolean Login(String username, String password) {
        _sessionToken = this.callLogin(username, password);
        if (_sessionToken.equals(NULL_SESSION)) {
            this._isLoggedIn = false;
        } else {
            this._isLoggedIn = true;
        }

        return _isLoggedIn;
    }

    public void Logout() {
        this._isLoggedIn = false;
        this.logout(this._sessionToken);
    }

    private String callLogin(java.lang.String user, java.lang.String password) {
        com.intel.healthcare.integration.authenticate.AuthenticateService service = new com.intel.healthcare.integration.authenticate.AuthenticateService();
        com.intel.healthcare.integration.authenticate.IAuthenticate port = service.getBasicHttpBindingIAuthenticate();
        return port.login(user, password);
    }

    private void logout(java.lang.String secureSessionToken) {
        com.intel.healthcare.integration.authenticate.AuthenticateService service = new com.intel.healthcare.integration.authenticate.AuthenticateService();
        com.intel.healthcare.integration.authenticate.IAuthenticate port = service.getBasicHttpBindingIAuthenticate();
        port.logout(secureSessionToken);
    }

    private Boolean callPing() {
        com.intel.healthcare.integration.userlookup.UserLookupService service = new com.intel.healthcare.integration.userlookup.UserLookupService();
        com.intel.healthcare.integration.userlookup.IUserLookup port = service.getBasicHttpBindingIUserLookup();
        return port.ping();
    }

}
