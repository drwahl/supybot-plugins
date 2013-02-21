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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class Youtube(callbacks.Plugin):
    """ interact with youtube.com in various ways """
    
    def ytsearch(self, irc, msg, args, string_of_search_terms):
        """ search for the supplied search term """
        import gdata.youtube
        import gdata.youtube.service
        answer_list = []
        list_of_search_terms = string_of_search_terms.split()
        yt_service = gdata.youtube.service.YouTubeService()
        yt_service.ssl = False #does not currently support ssl
        query = gdata.youtube.service.YouTubeVideoQuery()
        query.orderby = 'relevance'
        query.racy = 'include'
        for search_term in list_of_search_terms:
            new_term = search_term.lower()
            query.categories.append('/%s' % new_term)
        feed = yt_service.YouTubeQuery(query)
        video_title = str(feed.entry[0].media.title.text)
        video_url = str(feed.entry[0].media.player.url)
        seconds = int(feed.entry[0].media.duration.seconds)
        #pretty print video duration
        hours = seconds / 3600
        seconds -= 3600*hours
        minutes = seconds / 60
        seconds -= 60*minutes
        if hours == 0:
            video_duration = "%02d:%02d" % (minutes, seconds)
        else:
            video_duration = "%02d:%02d:%02d" % (hours, minutes, seconds)

        answer = '%s: %s - %s' % (video_title, video_url, video_duration)
        irc.reply(answer)

        def GetInHMS(seconds):
            """ convert seconds to something a little easier to read """
            hours = seconds / 3600
            seconds -= 3600*hours
            minutes = seconds / 60
            seconds -= 60*minutes
            if hours == 0:
                return "%02d:%02d" % (minutes, seconds)
            return "%02d:%02d:%02d" % (hours, minutes, seconds)

    ytsearch = wrap(ytsearch, ['text'])

Class = Youtube


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
