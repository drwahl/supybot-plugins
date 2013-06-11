#!/usr/bin/env python

#The purpose of this script is to return a space delimenated list of groups a
#user supplied username belongs to.

import sys
import ldap
import ldap.modlist
import time
import datetime
import calendar

ldap_server = 'ldap://ldap.example.com:389'
DM_password = 'password'

class ldapAccount:
    """ interact with Unix LDAP """

    def __init__(self):
        """ initialize object """

        self.ldapconn = ''
        self.result = {}
        self.user = {}

        self.baseDN = 'OU=people,dc=example,dc=com'
        try:
            self.ldapconn = ldap.initialize(ldap_server)
        except ldap.LDAPError:
            self.ldapconn.unbind()
            time.sleep(2)
            try:
                self.ldapconn = ldap.initialize(ldap_server)
            except ldap.LDAPError:
                self.ldapconn.unbind()
                time.sleep(2)
                try:
                    self.ldapconn = ldap.initialize(ldap_server)
                except ldap.LDAPError:
                    print "Unable to connect to LDAP server"
                    sys.exit(1)
        self.ldapconn.simple_bind_s('cn=Directory Manager', DM_password)
        
    def __call__(self):
        """ emulated object call """

        return self.user

    def __del__(self):
        """ cleanup ldap connection """

        self.ldapconn.unbind()
        return

    def populate(self, cmuser):
        """ discover properties for <user> """

        user_auth_info = {
            'password_source' : 'Unix LDAP',
            'locked' : 'Unknown',
            'expiry' : 'Unknown'
        }

        pw_policy = self.ldapconn.search_s(self.baseDN,ldap.SCOPE_ONELEVEL,'uid=%s' % cmuser, ['ds-pwp-password-policy-dn'])[0][1]
        test_locked = self.ldapconn.search_s(self.baseDN,ldap.SCOPE_ONELEVEL,'uid=%s' % cmuser, ['pwdFailureCountInterval'])
        print test_locked

        if len(pw_policy) < 1:
            user_auth_info['password_source'] = 'Unix LDAP'
        else:
            if 'ds-pwp-password-policy-dn' in pw_policy:
                if pw_policy['ds-pwp-password-policy-dn'][0] == 'cn=AD PTA Policy,cn=Password Policies,cn=config':
                    user_auth_info['password_source'] = 'Active Directory'
            else:
                user_auth_info['password_source'] = 'Unix LDAP'

        if user_auth_info['password_source'] == 'Unix LDAP':
            try:
                test_locked = self.ldapconn.search_s(self.baseDN,ldap.SCOPE_ONELEVEL,'uid=%s' % cmuser, ['ds-pwp-password-policy-dn'])
                print test_locked
                account_locked = self.ldapconn.search_s(self.baseDN,ldap.SCOPE_ONELEVEL,'uid=%s' % cmuser, ['asdf'])[0][1]
                if len(account_locked) < 1:
                    user_auth_info['locked'] = False
                    try:
                        passwd_expiry = self.ldapconn.search_s(self.baseDN,ldap.SCOPE_ONELEVEL,'uid=%s' % cmuser, ['ds-pwp-password-expiration-time'])[0][1]['ds-pwp-password-expiration-time'][0].split(".")[0]
                        expiry_date = time.strptime(passwd_expiry, "%Y %m %d %H %M %S")
                        tmp_date = (expiry_date[0], calendar.month_name[expiry_date[1]], expiry_date[2])
                        user_auth_info['expiry'] = "%s %s, %s" % (tmp_date[1], tmp_date[2], tmp_date[0])
                    except:
                        user_auth_info['expiry'] = 'Unknown'
                else:
                    user_auth_info['locked'] = True
            except:
                user_auth_info['locked'] = False

        return user_auth_info

    def exists(self, cmuser):
        """ determine if the given user exists """

        try:
            self.populate(cmuser)
            return 1
        except IndexError:
            return 0

if __name__ == "__main__":
    """ mainline of the script, if it is called from shell """

    import argparse

    cmd_parser = argparse.ArgumentParser(description='Query LDAP for the status of the users account (PTA/UNIX LDAP, Locked, expiry)')
    cmd_parser.add_argument('supplied_username', nargs='*')
    args = cmd_parser.parse_args()

    ldapuser = ldapAccount()
    print ldapuser.populate(args.supplied_username[0])
