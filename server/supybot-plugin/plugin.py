###
# Copyright (c) 2012, Roland Hieber
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

import os
from datetime import datetime
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class StratumMonitor(callbacks.Plugin):
  """Stratum 0 Open/Close Monitor"""
  pass

  NGINX_SITE_FILE = "/etc/nginx/sites-enabled/status.stratum0.org"
  NGINX_SITE_TEMPLATE = """server {
  root /srv/status.stratum0.org;
  index index.html index.htm;

  location / {
    access_log off;
    rewrite ^/status.png$ $scheme://$http_host/{{{STATUS}}}.png redirect;
    rewrite ^/favicon.ico$ $scheme://$http_host/{{{STATUS}}}.ico redirect;
    expires +5m;
  }
}
"""
  API_TEXT_FILE = "/srv/status.stratum0.org/status.txt"
  API_TEXT_TEMPLATE ="""Version: {{{VERSION}}}\r
IsOpen: {{{ISOPEN}}}\r
Since: {{{SINCE}}}\r
"""
  API_JSON_FILE = "/srv/status.stratum0.org/status.json"
  API_JSON_TEMPLATE = """{\r
  "version": "{{{VERSION}}}",\r
  "isOpen": {{{ISOPEN}}},\r
  "since": "{{{SINCE}}}"\r
}\r
"""
  API_XML_FILE = "/srv/status.stratum0.org/status.xml"
  API_XML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r
<status version="{{{VERSION}}}">\r
  <isOpen>{{{ISOPEN}}}</isOpen>\r
  <since>{{{SINCE}}}</since>\r
</status>\r
"""

  VERSION = "0.1"   ### Bump this for new API versions

  WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

  def __init__(self, irc):
    self.__parent = super(StratumMonitor, self)
    self.__parent.__init__(irc)

    self.isOpen = False
    self.since = datetime.now()

  def topicTimeString(self, date):
    return "%s, %s" % (self.WEEKDAYS[date.weekday()], date.strftime("%H:%M"))

  def replaceVariables(self, text):
    text = text.replace("{{{VERSION}}}", self.VERSION)
    text = text.replace("{{{SINCE}}}", self.since.isoformat())
    text = text.replace("{{{ISOPEN}}}", "true" if self.isOpen else "false")
    text = text.replace("{{{STATUS}}}", "open" if self.isOpen else "closed")
    return text

  def writeFile(self, filename, template):
    with open(filename, "w") as f:
      self.log.info("writing to file %s" % filename)
      t = self.replaceVariables(template)
      f.write(t)

  def writeFiles(self):
    self.writeFile(self.NGINX_SITE_FILE, self.NGINX_SITE_TEMPLATE)
    self.writeFile(self.API_TEXT_FILE, self.API_TEXT_TEMPLATE)
    self.writeFile(self.API_JSON_FILE, self.API_JSON_TEMPLATE)
    self.writeFile(self.API_XML_FILE, self.API_XML_TEMPLATE)
    r = os.system("sudo killall -HUP nginx"); # NOTE: must be in sudoers to do that!

  def spaceopen(self, irc, msg, args):
    """
    This command is for internal use only. Any unauthorized use is prohibited.
    If you use it anyhow, this command will eat your dog, fry it and quarter it
    (in exactly this order). If you have no dog, it will take the Nyan cat
    instead.
    """
    self.since = datetime.now()
    self.isOpen = True;
    self.writeFiles()
    irc.reply("Space ist offen (Stand: %s)" % self.topicTimeString(self.since),
      prefixNick = False)

  spaceopen = wrap(spaceopen)

  def spaceclosed(self, irc, msg, args):
    """
    This command is for internal use only. Any unauthorized use is prohibited.
    If you use it anyhow, this command will eat your dog, fry it and quarter it
    (in exactly this order). If you have no dog, it will take the Nyan cat
    instead.
    """
    self.since = datetime.now()
    self.isOpen = False;
    self.writeFiles()
    irc.reply("Space ist zu (Stand: %s)" % self.topicTimeString(self.since),
      prefixNick = False)

  spaceclosed = wrap(spaceclosed)

  def spacestatus(self, irc, msg, args):
    if(self.isOpen):
      irc.reply("Space ist offen (seit %s)" % self.topicTimeString(self.since))
    else:
      irc.reply("Space ist zu (seit %s)" % self.topicTimeString(self.since))

  spacestatus = wrap(spacestatus)

Class = StratumMonitor

# vim:set shiftwidth=2 softtabstop=2 expandtab textwidth=79:
