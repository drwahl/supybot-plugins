###
# Copyright (c) 2011, D. Wahlstrom
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
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import SOAPpy
import urllib2
import urllib
import threading
import time
import re
import simplejson as json

class Jira(callbacks.Plugin):
    def __init__(self, irc):
        self.__parent = super(Jira, self)
        self.__parent.__init__(irc)

    def callCommand(self, method, irc, msg, *L, **kwargs):
        try:
            self.__parent.callCommand(method, irc, msg, *L, **kwargs)
        except utils.web.Error, e:
            irc.error(str(e))

    def _jiraFetchData(self, irc, msg, ticket):

        server = 'http://jira.example.com'
        username = 'irc'
        password = 'ircbot'
        
        soap = SOAPpy.WSDL.Proxy('%s/rpc/soap/jirasoapservice-v2?wsdl' % server)
        auth = soap.login(username, password)

        try:
            result = soap.getIssue(auth, ticket)
            valid = True
        except:
            valid = False

        if not valid:
            irc.reply('invalid ticket: ' + str(ticket))
        else:
            tmp_statuses = soap.getStatuses(auth)
            tmp_priorities = soap.getPriorities(auth)

            status = {}
            for i in tmp_statuses:
                status[i['id']] = i['name']

            priorities = {}
            for i in tmp_priorities:
                priorities[i['id']] = i['name']

            url = '%s/browse/%s' % (server, result['key'])

            return[url, result['summary'], result['reporter'], result['assignee'], status[result['status']], priorities[result['priority']]]

#           answer = '%s, Summary: %s, Reporter: %s, Assignee: %s, Status: %s, Priority: %s' % ( url, result['summary'], result['reporter'], result['assignee'], status[result['status']], priorities[result['priority']] )


    def doPrivmsg(self, irc, msg):
        #msg.args[0] is the channel name
        #msg.args[1] is the message text
        txt = msg.args[1].split()
        #regex match for project queus
        jiraRegex = r'((?i)\bqueue1\b|\bqueue2\b|\bqueue3\b)+(-)+(\d+)'
        for word in txt:
            jiraMatch = re.match(jiraRegex, word)
            if jiraMatch is not None:
                ticketid = jiraMatch.group()
                jiraData = self._jiraFetchData(irc, msg, ticketid)
                if jiraData is not None:
                    (url, summary, reporter, assignee, status, priority) = jiraData
                    responseTxt = '%s, Summary: %s, Reporter: %s, Assignee: %s, Status: %s, Priority: %s' % ( url, summary, reporter, assignee, status, priority )
                    irc.reply(responseTxt, prefixNick=False)

Class = Jira

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
