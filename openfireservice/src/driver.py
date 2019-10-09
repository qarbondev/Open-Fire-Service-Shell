from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from cloudshell.api.cloudshell_api import CloudShellAPISession


from cloudshell.logging.qs_logger import get_qs_logger
from data_model import *  # run 'shellfoundry generate' to generate data model classes

# requests package to drive REST API admin plug-in for Openfire Server
import requests
# Use sleekxmpp for additional access to Openfire using xmpp/Jabber protocol (used in sending chat messages for chat rooms, etc.)
# See www.sleekxmpp.com
from sleekxmpp import ClientXMPP

# Used for parsing XML responses from ClientXMPP class methods
import xml.etree.ElementTree as ET
import json
import time
from dateutil.parser import *

# class used to monitor messages sent direct to a chat room (outside of CloudShell)
# See below for main Shell class
class MucBot(ClientXMPP):

    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password, session, context, room, user, xmpp_domain):
        ClientXMPP.__init__(self, jid, password)

        self.res_id = context.reservation.reservation_id
        self.context = context
        self.session = session
        self.room = room
        self.user = user
        self.room_name = session.GetReservationDetails(reservationId=self.res_id).ReservationDescription.Name
        self.domain = xmpp_domain

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
        self.session.WriteMessageToReservationOutput(self.res_id,
                                                "\nMonitoring chatroom \"%s\" for messages" % self.room_name)

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

        session = self.session
        sender=msg['mucnick']
        body=msg['body']

        session.WriteMessageToReservationOutput(self.res_id, "\nChatroom message: (%s) \"%s\"" % (sender, body))

# Main shell class
class OpenfireserviceDriver (ResourceDriverInterface):

    def __init__(self):
        """
        ctor must be without arguments, it is created with reflection at run time
        """
        pass

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    # Get CloudShell server, credentials and port - used to drive Sandbox API to attach file to sandbox below
    def __get_cloudshell_server_details(self, context, sess):
        """
        :param ResourceCommandContext context: the context the command runs on
        """

        resource=Openfireservice.create_from_context(context)
        return resource.cloudshell_user, sess.DecryptPassword(resource.cloudshell_password).Value, resource.cloudshell_server, resource.cloudshell_api_port

    # Get Openfire server details
    def __get_openfire_server_details(self, context, sess):
        """
        :param ResourceCommandContext context: the context the command runs on
        """
        resource=Openfireservice.create_from_context(context)
        return resource.user, sess.DecryptPassword(resource.password).Value, resource.server, resource.port

    def __get_session(self, context):
        """
        :param ResourceCommandContext context: the context the command runs on
        """
        sess = CloudShellAPISession(host=context.connectivity.server_address,
                                       token_id=context.connectivity.admin_auth_token,
                                       domain=context.reservation.domain)
        return sess

    # Construct Openfire REST API URL
    def __get_rest_api_base_url(self, server, port):
        """
        :param ResourceCommandContext context: the context the command runs on
        """
        return "http://" + server + ":" + port + "/plugins/restapi/v1"

    # Get XMPP domain property of Openfire server
    def __get_xmpp_domain(self, server, port, user, password):

        p = requests.get(url="http://%s:%s/plugins/restapi/v1/system/properties" % (server, port), auth=(user, password))
        root = ET.fromstring(p.content)
        for prop in root:
            Key = prop.attrib.get('key')
            if Key == "xmpp.domain":
                return prop.attrib.get('value')

    # Invoked to continously monitor the chatroom for messages sent outside of CloudShell
    def monitor_chatroom(self, context):
        """
        :param ResourceCommandContext context: the context the command runs on
        """
        # Get context
        session = self.__get_session(context)
        res_id = context.reservation.reservation_id

        admin_user, admin_password, api_server, api_port=self.__get_openfire_server_details(context, session)
        xmpp_domain = self.__get_xmpp_domain(server=api_server, port=api_port, user=admin_user, password=admin_password)
        room = '%s@conference.%s' % (res_id, xmpp_domain)

        # Construct full Jabber user id
        JID = "%s@%s" % (admin_user, xmpp_domain)
        # Create instance of class to monitor messages in named room
        xmpp = MucBot(JID, admin_password, session, context, room, admin_user, xmpp_domain)
        # Plug in used by REST API
        xmpp.register_plugin('xep_0045')
        xmpp.connect(address=(api_server, '5222'))
        # Run above commands
        xmpp.process(block=True)

        pass

    # Send message to sandbox chat room
    def send_chatroom_message(self, context, message):

        # Get context
        session = self.__get_session(context)
        res_id = context.reservation.reservation_id
        current_user = context.reservation.running_user

        admin_user, admin_password, api_server, api_port=self.__get_openfire_server_details(context, session)

        # Chatroom name is current sandbox name
        chatroom_name = session.GetReservationDetails(reservationId=res_id).ReservationDescription.Name
        # Chatroom ID is reservation id
        chatroom_id = res_id
        # Get XMPP domain value
        xmpp_domain = self.__get_xmpp_domain(server=api_server, port=api_port, user=admin_user, password=admin_password)
        # Construct full Jabber user id
        JID = "%s@%s" % (admin_user, xmpp_domain)

        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "\nSending message to chat room \"%s\" as %s" % (chatroom_name, current_user) )
        xmpp = ClientXMPP(jid=JID, password=admin_password)
        xmpp.register_plugin('xep_0045')
        conn = xmpp.connect(use_ssl=False, use_tls=False, address=(api_server, '5222'))

        room = '%s@conference.%s' % (chatroom_id, xmpp_domain)
        # need to join chat room before sending message
        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "    Joining room")
        xmpp.plugin['xep_0045'].joinMUC(room, current_user, wait=True, )

        # Send message to room
        xmpp.send_message(mtype='groupchat', mbody=message, mto=room, mnick=current_user)

        # Run commands above
        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "    Sending message \"%s\"" % message)
        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Completed" )
        xmpp.process(block=False)

        # Ensure we have enough time to send the message before disconnecting
        time.sleep(5)
        xmpp.disconnect()

        pass

    # Should be invoked when Sandbox starts during Setup
    def create_chatroom(self, context):
        """
        :param ResourceCommandContext context: the context the command runs on
        """
        # Get context
        session = self.__get_session(context)
        res_id = context.reservation.reservation_id
        # Get sandbox name
        sandbox_name = session.GetReservationDetails(reservationId=res_id).ReservationDescription.Name
        # Get Openfire Server details
        admin_user, admin_password, api_server, api_port=self.__get_openfire_server_details(context, session)

        # Create new chat room based on reservation name and id
        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "\nCreating new chat room \"" + sandbox_name + "\":")
        # persistent value ensures chat room is not temporary, i.e. deletes automatically when users leave the room
        payload = { "roomName": res_id, "naturalName": sandbox_name, "description": "Created by CloudShell Openfire Service", "persistent": "true" }

        try:
            create_new_chatroom = requests.post(url=self.__get_rest_api_base_url(api_server, api_port) + "/chatrooms", auth=(admin_user, admin_password), json=payload)
        except:
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, "\n    Error creating new chatroom")

        # Add sandbox permitted users as member users to the room
        permitted_users = session.GetReservationDetails(reservationId=res_id).ReservationDescription.PermittedUsers
        for permitted_user in permitted_users:
            # Add new own user to chat room if not owner
            if permitted_user != context.reservation.owner_user:
                add_user_member = requests.post(url="%s/chatrooms/%s/members/%s" % (self.__get_rest_api_base_url(api_server, api_port), res_id, permitted_user), auth=(admin_user, admin_password))
                session.WriteMessageToReservationOutput(res_id, "    Added member %s" % (permitted_user))
        session.WriteMessageToReservationOutput(res_id, "Completed")

        pass

    # Should be invoked when Sandbox ends during Teardown
    def delete_chatroom(self, context):
        """
        :param ResourceCommandContext context: the context the command runs on
        """

        # Get context
        session = self.__get_session(context)
        res_id = context.reservation.reservation_id
        # Get sandbox name
        sandbox_name = session.GetReservationDetails(reservationId=res_id).ReservationDescription.Name
        # Get Openfire Server details
        admin_user, admin_password, api_server, api_port=self.__get_openfire_server_details(context, session)

        session.WriteMessageToReservationOutput(res_id, "\nDeleting sandbox chat room \"" + sandbox_name + "\":")
        delete_chatroom = requests.delete(url=self.__get_rest_api_base_url(api_server, api_port) + "/chatrooms/" + res_id, auth=(admin_user, admin_password))
        session.WriteMessageToReservationOutput(res_id, "Completed")

        pass

    # Broadcasts message to all users connected to the OpenFire server
    def broadcast_message(self, context, message):
        """
        :param ResourceCommandContext context: the context the command runs on
        """

        # Get context
        session = self.__get_session(context)
        res_id = context.reservation.reservation_id
        admin_user, admin_password, api_server, api_port=self.__get_openfire_server_details(context, session)

        payload = { "body": message }
        session.WriteMessageToReservationOutput(res_id, "\nBroadcasting to all users:\n" + "  message: \"" + message + "\"")
        broadcast_message = requests.post(url=self.__get_rest_api_base_url(api_server, api_port) + "/messages/users", auth=(admin_user, admin_password), json=payload)
        session.WriteMessageToReservationOutput(res_id, "Completed")

        pass

    # Report on who is owner(s) and members(s) of chatroom
    def show_chatroom_users(self, context):
        """
        :param ResourceCommandContext context: the context the command runs on
        """

        # Get context
        session = self.__get_session(context)
        admin_user, admin_password, api_server, api_port=self.__get_openfire_server_details(context, session)

        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "\nListing different users in sandbox chat room:")
        chatroom_info = requests.get(url=self.__get_rest_api_base_url(api_server, api_port) + "/chatrooms/" + context.reservation.reservation_id, auth=(admin_user, admin_password))
        room_root = ET.fromstring(chatroom_info.content)

        # List owners in returned chatroom XML
        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "  Owner(s):")
        for o in room_root.iter('owner'):
            owner_name, domain = o.text.split('@')
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, "    " + owner_name)

        # List members in returned chatroom XML
        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "  Member(s):")
        for m in room_root.iter('member'):
            member_name, domain = m.text.split('@')
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, "    " + member_name)

        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Completed")

        pass

    # Get list of messages, senders and date/time stamps starting with earliest
    def get_chatroom_message_history(self, context):
        """
        :param ResourceCommandContext context: the context the command runs on
        """

        # Get context
        session = self.__get_session(context)
        admin_user, admin_password, api_server, api_port=self.__get_openfire_server_details(context, session)

        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "\nGetting message history for sandbox chat room:")

        chatroom_message_history = requests.get(url=self.__get_rest_api_base_url(api_server, api_port) + "/chatrooms/" + context.reservation.reservation_id + "/chathistory", auth=(admin_user, admin_password))
        messages = ET.fromstring(chatroom_message_history.text)
        for o in messages.findall('message'):
            # Convert RFC format dates into plain text
            dte_string = parse(o.find('delay_stamp').text).ctime().replace('  ', ' ')
            sender = o.find('from').text.split("/", 1)[1]
            sender = sender.split("@")[0]
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, "  (" + dte_string + ") " + sender + ": \"" + o.find('body').text + "\"\n")
        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Completed")

        pass

    # Build history of chatroom messages and then attach to sandbox
    def attach_chatroom_message_history(self, context):
        """
        :param ResourceCommandContext context: the context the command runs on
        """

        # Get context
        session = self.__get_session(context)
        admin_user, admin_password, api_server, api_port=self.__get_openfire_server_details(context, session)

        session.WriteMessageToReservationOutput(context.reservation.reservation_id, "\nAttaching message history for sandbox chat room:")

        chatroom_message_history = requests.get(url=self.__get_rest_api_base_url(api_server, api_port) + "/chatrooms/" + context.reservation.reservation_id + "/chathistory", auth=(admin_user, admin_password))
        file = open("C:\Temp\messages.txt", "w")
        messages = ET.fromstring(chatroom_message_history.text)
        for o in messages.findall('message'):
            # Convert RFC format dates into plain text
            dte_string = parse(o.find('delay_stamp').text).ctime().replace('  ', ' ')
            sender = o.find('from').text.split("/", 1)[1]
            sender = sender.split("@")[0]
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, "  (" + dte_string + ") " + sender + ": \"" + o.find('body').text + "\"\n")
            file.write("(" + dte_string +") " + sender + ": \"" + o.find('body').text + "\"\n")
        file.close()

        cs_admin_user, cs_admin_password, cs_server, cs_api_port=self.__get_cloudshell_server_details(context, session)

        domain = context.reservation.domain

        # attach zip file to sandbox
        api_base_url = "http://%s:%s/Api" % (cs_server, cs_api_port)

        # Login method
        login_hdrs = {'content-type': "application/json", 'cache-control': "no-cache"}
        login_payload = r'{"Username": "' + cs_admin_user + '", "Password": "' + cs_admin_password + '", "Domain": "' + domain + '"}'
        login_result = requests.put(api_base_url + "/Auth/Login", data=login_payload, headers=login_hdrs)

        auth_code = "Basic {0}".format(login_result.content[1:-1])

        with open("C:\Temp\messages.txt", "rb") as attached_file:
            attach_file_hdrs = {"Authorization": auth_code}
            attach_payload = {"reservationId": context.reservation.reservation_id, "saveFileAs": "messages.txt",
                              "overwriteIfExists": "true"}
            attach_file_result = requests.post(api_base_url + "/Package/AttachFileToReservation",
                                               headers=attach_file_hdrs,
                                               data=attach_payload,
                                               files={'QualiPackage': attached_file})

        result = json.loads(attach_file_result.content)
        if (result['Success']):
            session.WriteMessageToReservationOutput(context.reservation.reservation_id, "Completed")
        else:
            raise KeyError('Error in attaching message file: %r' % result['ErrorMessage'])

        pass

