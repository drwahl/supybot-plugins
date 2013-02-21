###
# Copyright (c) 2013, David Wahlstrom
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

import group_query

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class Getent(callbacks.Plugin):
    def group(self, irc, msg, args, username=''):
        """Return a list of groups the user belongs"""

        answer = []
        ldapuser = group_query.ldapAccount()
        if ldapuser.exists(username):
            answer = ' '.join(ldapuser.get_groups())
        else:
            answer = "User %s does not exist" % username
        irc.reply(answer)
    group = wrap(group, ['text'])

    def uid(self, irc, msg, args, username=''):
        """Return a list of groups the user belongs"""

        answer = []
        ldapuser = group_query.ldapAccount()
        if ldapuser.exists(username):
            answer = ldapuser.get_field('uidNumber')
        else:
            answer = "User %s does not exist" % username
        irc.reply(answer)
    uid = wrap(uid, ['text'])

    def groups(self, irc, msg, args):
        """Return a list of groups the user belongs"""

        answer = []
        ldapuser = group_query.ldapAccount()
        ldapuser.populate('')
        all_groups = ldapuser.get_all_groups()
        irc.reply(all_groups)
    groups = wrap(groups)

Class = Getent

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79: