# jabberlogging.py
# Version 1.0
# A really simple Python logging module Handler that sends log
# messages via XMPP. Compatible with Jabber and Google Talk.
# (c) Alex Macmillan 2009.

# If you like you may consider this work licensed under WTFPL 2.0.
# INSTALLATION and CONFIGURATION
# 1. Install dependencies:
#    $ easy_install dnspython
#    $ easy_install xmpppy
# 2. Copy moononstick.py to your Python project's directory.
# 3. Set the Jabber ID that messages will be sent from.
#    You can register the logger a new Jabber ID for this 
#    purpose at, for instance, jabber.org.
#    eg. yourname_devlogger@jabber.org

MY_JID = "tronbot@aura.local"

# 4. Set the sending Jabber ID's password

MY_PASSWORD = "tr0nr0cks"

# 5. Set the Jabber ID that you want to receive messages.
#    eg. yourname@gmail.com

DEST_JID = "arnaudsj@aura.local"

# 6. In your application, add:
#    import moononstick
#    moononstick.init_jabber_logging()

# You're done.

# Note: You may want to use an instant messenger to log in with your
# new dev jabber id and make sure it's friends with the jabber id that
# will be receiving log messages first, to ensure that the dev account
# is allowed to send messages to the receiving account.


import logging
import sys,os,xmpp,time

tojid=DEST_JID

jidparams={
    'jid' : MY_JID,
    'password' : MY_PASSWORD
}

# Some cheap-ass globals.
jid=xmpp.protocol.JID(jidparams['jid'])
cl=xmpp.Client(jid.getDomain())

# This is the format of messages that you will receive.
jabberformatter = logging.Formatter("*%(asctime)s* - %(name)s - *%(levelname)s*\n%(message)s")

def connect():
    con=cl.connect()
    if not con:
        #print 'MoonOnStick: could not connect!'
        sys.exit()
    #print 'MoonOnStick: connected with',con
    auth=cl.auth(jid.getNode(),jidparams['password'],resource=jid.getResource())
    if not auth:
        #print 'MoonOnStick: could not authenticate!'
        sys.exit()
    #print 'MoonOnStick: authenticated using',auth

def present():
    cl.sendInitPresence(requestRoster=0)

def message(text):
    id=cl.send(xmpp.protocol.Message(tojid,text))
    #print 'MoonOnStick: sent message with id',id

def disconnect():
    cl.disconnect()

class JabberHandler(logging.Handler):
    """Handler that sends all received messages via XMPP to a willing recipient."""
    def __init__(self):
        logging.Handler.__init__(self)
        # Create a Jabber connection.
        connect()
        present()

    def emit(self, record):
        message(self.format(record))

def init_jabber_logging():
    # Get a Jabber handler.
    jh = JabberHandler()
    # Set it's formatter to the jabber formatter.
    jh.setFormatter(jabberformatter)
    # Attach to the root logger.
    r = logging.getLogger()
    r.addHandler(jh)
    # Set the root logger to log all DEBUG messages and above.
    r.setLevel(logging.WARNING)