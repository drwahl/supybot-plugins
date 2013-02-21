###
# Copyright (c) 2011, David Wahlstrom
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import xmlrpclib

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

xenserver = 'https://xenserver01.examplecom/'
xenserver_username = 'root'
xenserver_password = 'root'

class Xen(callbacks.Plugin):
    def xenupdatecache(self, irc, msg, args):
        """ Init/Update xen info cache """
        xenapi = xmlrpclib.Server(xenserver)
        xensession = xenapi.session.login_with_password(xenserver_username, xenserver_password)['Value']
        self.vmcache = xenapi.VM.get_all_records(xensession)['Value']
        xenapi.session.logout(xensession)
        irc.reply('Xen cache updated')
    xenupdatecache = wrap(xenupdatecache)

    def vmsearch(self, irc, msg, args, name):
        """ List VMs matching the search parameters """
        answer = []
        for vm in self.vmcache:
            if name in self.vmcache[vm]['name_label']:
                answer.append(self.vmcache[vm]['name_label'])
        irc.reply(answer)
    vmsearch = wrap(vmsearch, ['text'])

    def vmpowerstate(self, irc, msg, args, name):
        """ Display the power status of a given VM """
        answer = []
        uuids = []
        vms = {}
        for id in self.vmcache:
            if name in self.vmcache[id]['name_label']:
                vms[id] = { 'name' : self.vmcache[id]['name_label'] ,
                            'powerstate' : self.vmcache[id]['power_state']}
        for vm in vms:
            answer.append(vms[vm])
        irc.reply(answer)
    vmpowerstate = wrap(vmpowerstate, ['text'])
        
Class = Xen


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
