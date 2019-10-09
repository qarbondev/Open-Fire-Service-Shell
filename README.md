# OpenFire Server Custom Service Shell

## Introduction
This custom service shell provides an integration with the OpenFire RealTime Collaboration (RTC) server whose details can be found @ https://www.igniterealtime.org/projects/openfire/

OpenFire uses the only widely adopted open protocol for instant messaging, XMPP (also called Jabber). At its core is the concept of a conference or chat room. The idea behind this integration is to allow a chat room to be created by this service for each sandbox. Messages can be entered directly into the chat room via a client such as Spark (for example, the Instant Messaging client @ https://www.igniterealtime.org/projects/spark/index.jsp) or via a command from this Shell. 

## CloudShell and OpenFire Compatibility
This service shell was developed and tested against CloudShell 9.2 GA. There is no reason why it would not work with 9.3 GA although it would require an update to the requirements.txt file as documented @ https://devguide.quali.com/orchestration/9.3.0/getting-started.html to reflect the use of a later version of the the cloudshell-orch-core package

The integration was developed and tested against OpenFire Server 4.4.1

## Setup
The following steps should be taken when using this Shell:
1. Import this Shell into CloudShell.
2. Set up the OpenFire Server. It can be installed on the same host as the Quali Server or on a separate machine. The download link is at @ https://www.igniterealtime.org/downloads/index.jsp#openfire (we developed and tested against v4.4.1)
3. Install the REST API Admin plug-in for OpenFire (this is the one written by Roman Soldatow).

![OpenFire Shell Service REST API Plug In](https://user-images.githubusercontent.com/18084644/66498529-23f95100-eab6-11e9-847d-d2006709a0b1.PNG)

4. Log in to the Web GUI for the OpenFire server (for example, http://localhost:9090). Move to the "Server" toolbar and then "Server Settings" under this. You should see "REST API" on the bottom left. Select this and then Enable the plug-in with basic authentication.


5. Download and install the Spark client from https://www.igniterealtime.org/downloads/index.jsp#openfire. Log in and test the connectivity to the OpenFire server.

## Operational Usage
First, you need to add two instances of the service to a blueprint. Since service shells do not allow concurrent commands, this is necessary since one command needs to be running all the time - the one that monitors a chat room for messages entered outside of CloudShell in order to echo them in the sandbox.

We suggest you name the instances something like "Chat Room Message Monitor" and "Chat Room Functions". Ensure that the properties are entered correctly. Essentially, you need to identify the admin account and location of the OpenFire Server and also the same for CloudShell.

Reserve your blueprint. Once Active, you should create a chatroom for the sandbox using the "Create Sandbox Chat Room" command. Notice in the Spark client and/or the OpenFire Server web GUI, there is now a new Group Chat room. The owner will be set as the admin user defined in the service properties for OpenFire. The members will reflect the permitted users of the sandbox. It is important that all users that need access to this chat room should be made Permitted Users.

In the other service instance (let us call it "Chat Room Message Monitor", click on the "

## Suggested Improvements
If the sandbox name changes or any of its permitted users, the chat room name or its room members respectively are not automatically updated. An option to auto reflect such changes after a change should be offered perhaps.
