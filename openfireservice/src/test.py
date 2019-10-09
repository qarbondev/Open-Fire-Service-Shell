from sleekxmpp import ClientXMPP

class MucBot(ClientXMPP):

    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)

        self.res_id = "9dedadc8-bb9b-4849-9909-ed001ed6aff0"
        self.room = "9dedadc8-bb9b-4849-9909-ed001ed6aff0"
        self.user = "admin"
        self.room_name = "Home Office Network Sandbox"
        self.domain = "desktop-9j2jd3l.home"

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("groupchat_message", self.muc_message)


    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.user,
                                        wait=True)
        #self.session.WriteMessageToReservationOutput(self.res_id,
                                               #"\nMonitoring chatroom \"%s\" for messages" % self.room_name)

    def muc_message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """

        #session = self.session
        sender=msg['from']
        msg.
        body=msg['body']
        fro = msg.find('from').text
        # Echo message to sandbox Output window - needs improving as sender is printed long style, e.g. : 3b47d0a3-b94f-483b-ad2f-0c44c6abd0b8@conference.desktop-9j2jd3l.home/mary
        # For some reason I cannot parse the sender varible using split(), for example
        #session.WriteMessageToReservationOutput(self.res_id, "\nChatroom message: (%s) \"%s\"" % (fro, body))

if __name__ == "__main__":
        xmpp = MucBot("admin@desktop9j2jd3l.home", "Quali92")
        # Plug in used by REST API
        xmpp.register_plugin('xep_0045')
        xmpp.connect(address=('localhost', '5222'))
        # Run above commands
        xmpp.process(block=True)

