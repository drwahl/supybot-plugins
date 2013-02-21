#!/usr/bin/env python

#The purpose of this script is to return a space delimenated list of groups a
#user supplied username belongs to.

import sys
import ldap
import ldap.modlist
import time

class ldapAccount:
    """ interact with Unix LDAP """

    def __init__(self):
        """ initialize object """

        self.ldapconn = ''
        self.result = {}
        self.user = {}

        self.baseDN = 'OU=people,DC=example,DC=com'
        self.groupDN = 'OU=group,DC=example,DC=com'
        try:
            self.ldapconn = ldap.initialize('ldap://ldap.example.com:1389')
        except ldap.LDAPError:
            self.ldapconn.unbind()
            time.sleep(2)
            try:
                self.ldapconn = ldap.initialize('ldap://ldap.example.com:1389')
            except ldap.LDAPError:
                self.ldapconn.unbind()
                time.sleep(2)
                try:
                    self.ldapconn = ldap.initialize('ldap://ldap.example.com:1389')
                except ldap.LDAPError:
                    print "Unable to connect to LDAP server"
                    sys.exit(1)
        
    def __call__(self):
        """ emulated object call """

        return self.user

    def __del__(self):
        """ cleanup ldap connection """

        self.ldapconn.unbind()
        return

    def populate(self, lduser):
        """ discover properties for <user> """

# the ldap record should look something like this:
#{'shadowFlag': ['0'], 
#'cn': ['John Doe'], 
#'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'ldappublickey', 'shadowAccount', 'posixAccount', 'top'], 
#'loginShell': ['/bin/bash'], 
#'shadowWarning': ['7'], 
#'uidNumber': ['5053'], 
#'shadowMax': ['99999'], 
#'gidNumber': ['1024'], 
#'gecos': ['John Doe'], 
#'sn': ['Jensen'], 
#'homeDirectory': ['/home/jdoe'], 
#'shadowLastChange': ['12277'], 
#'uid': ['jdoe']}
        self.user['valid'] = False
        self.all_basedn_records = self.ldapconn.search_s(self.baseDN,ldap.SCOPE_SUBTREE,'(objectClass=*)')
        for dn,entry in self.all_basedn_records:
            #note: dn is case sensative in LDAP, but we're ignoring that here,
            #      so false positives may arrise with this dn.lower()
            if lduser in dn.lower():
                self.user = entry
                self.user['dn'] = dn
                self.user['valid'] = True


        groups = []
        self.all_groups = self.ldapconn.search_s(self.groupDN,ldap.SCOPE_SUBTREE,'(objectClass=*)')

        if 'gidNumber' in self.user:
            for groupid in self.user['gidNumber']:
                for dn in self.all_groups:
                    if 'gidNumber' in dn[1]:
                        if groupid in dn[1]['gidNumber']:
                            if 'ou' in dn[1]:
                                groups.append(dn[1]['ou'][0])
                            else:
                                groups.append(dn[1]['cn'][0])

        #get a list of the non-nested groups the user is apart of
        for dn in self.all_groups:
            if 'memberUid' in dn[1]:
                if lduser in dn[1]['memberUid']:
                    groups.append(dn[1]['cn'][0])
            if 'uniqueMember' in dn[1]:
                lduser_uid = "uid=%s,ou=people,dc=example,dc=com" % lduser
                if lduser_uid in dn[1]['uniqueMember']:
                    groups.append(dn[1]['cn'][0])

        #unwind the groups the user is appart of to determine if any of them are
        #nested in other groups
        changed = True
        while changed == True:
            for nested_group in groups:
                for dn in self.all_groups:
                    if 'memberUid' in dn[1]:
                        if nested_group in dn[1]['memberUid']:
                            changed = True
                            groups.append(dn[1]['cn'][0])
                    if 'uniqueMember' in dn[1]:
                        nested_group_uid = "uid=%s,ou=groups,dc=example,dc=com" % nested_group
                        if nested_group_uid in dn[1]['uniqueMember']:
                            changed = True
                            groups.append(dn[1]['cn'][0])
            changed = False

        self.user['groups'] = dict(map(None,groups,[])).keys()

        return self.user

    def get_result(self):
        """ return the results from the populate function """

        return self.user

    def get_field(self, field):
        """ return field not defined elsewhere. will usually return a list """

        try:
            answer = self.user[field]
            if type(answer) == list:
                if len(answer) == 1:
                    return answer[0]
                else:
                    return answer
            else:
                return answer
        except KeyError:
            raise KeyError

    def get_groups(self):
        """ return the groups which the user is apart of """

        return self.user['groups']

    def get_all_groups(self):
        """ return the groups which the user is apart of """

        ldap_group_cns = []
        for group in self.all_groups:
            friendly_group_name = group[0].split(',')[0].split('=')[1]
            ldap_group_cns.append(friendly_group_name)

        ldap_groups = dict(map(None,ldap_group_cns,[])).keys()
        final_groups = ' '.join(ldap_groups)

        return final_groups

    def exists(self, lduser):
        """ determine if the given user exists """

        if not self.user:
            self.populate(lduser)

        try:
            if lduser in self.get_field('uid'):
                return 1
        except KeyError:
            pass

        try:
            if lduser in self.get_field('name'):
                return 1
        except KeyError:
            return 0

    def valid(self):
        """ return whether this user has a valid ldap account """

        return self.user['valid']

if __name__ == "__main__":
    """ mainline of the script, if it is called from shell """

    import argparse

    cmd_parser = argparse.ArgumentParser(description='If a username is supplied, query LDAP for the groups the user belongs to.  With the -a flag, display all groups in LDAP')
    cmd_parser.add_argument('-a', '--all', dest='query_all_groups', action='store_true', help='Return a definitive list of the all groups in LDAP.', required=False, default=False)
    cmd_parser.add_argument('supplied_username', nargs='*')
    args = cmd_parser.parse_args()

    ldapuser = ldapAccount()
    if args.query_all_groups:
        ldapuser.populate('')
        print '\n'.join(ldapuser.get_all_groups())
        sys.exit(0)

    try:
        username = args.supplied_username[0]
    except:
        username = raw_input('Username to query: ')

    if not username:
        print "Please supply a username"
        sys.exit(1)

    if not ldapuser.exists(username):
        print "User %s does not exist in LDAP" % username
    else:
        print ' '.join(ldapuser.get_groups())

    print ldapuser.get_field('uidNumber')
