###
# Copyright (c) 2014, David Wahlstrom
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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import ibquery

class Infoblox(callbacks.Plugin):
    def host(self, irc, msg, args, hostname):
        """host <hostname>

           Searches (substring matching) for records with the supplied hostname.
        """
        answer = []
        tmp_answer = []
        query = ibquery.host_query(hostname)
        if len(query) > 0:
            for key in query.keys():
                tmp_answer.append('%s: %s' % (key, ', '.join(map(str, query[key]))))
            answer = ' | '.join(tmp_answer)
        else: 
            answer = '%s not found in database' % hostname
        irc.reply(answer)
    host = wrap(host, ['text'])

    def vlan(self, irc, msg, args, ip):
        """vlan <ip>

           Returns the name and description of the network the IP belongs to.
        """
        answer = False
        result = ibquery.vlan_query(ip)
        answer = '%s - %s' % (result['network'], result['comment'])
        irc.reply(answer)
    vlan = wrap(vlan, ['text'])


Class = Infoblox


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
