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

![OpenFire Shell Service REST API Enable](https://user-images.githubusercontent.com/18084644/66498860-b0a40f00-eab6-11e9-8676-3f0385ee367f.PNG)

5. Download and install the Spark client from https://www.igniterealtime.org/downloads/index.jsp#openfire. Log in and test the connectivity to the OpenFire server.

## Operational Usage
### Adding Services to a blueprint
First, you need to add two instances of the service to a blueprint. Since service shells do not allow concurrent commands, this is necessary since one command needs to be running all the time - the one that monitors a chat room for messages entered outside of CloudShell in order to echo them in the sandbox.

We suggest you name the instances something like "Chat Room Monitor" and "Chat Room Service". Ensure that the properties are entered correctly into both services. Essentially, you need to identify the admin account and location of the OpenFire Server and also the same for CloudShell.

![Chatroom Blueprint](https://user-images.githubusercontent.com/18084644/66499146-25774900-eab7-11e9-9e42-bf93d9c319b7.PNG)

### Reserving a blueprint and creating the chat room for the sandbox
Reserve your blueprint. Once Active, you should create a chatroom for the sandbox using the "Create Sandbox Chat Room" command. Notice in the Spark client and/or the OpenFire Server web GUI, there is now a new Group Chat room. The owner will be set as the admin user defined in the service properties for OpenFire. The members will reflect the permitted users of the sandbox. It is important that all users that need access to this chat room should be made Permitted Users.

![Sandbox Name](https://user-images.githubusercontent.com/18084644/66499702-3b393e00-eab8-11e9-91c5-756ebc351ed9.PNG)

![Create Chat Room](https://user-images.githubusercontent.com/18084644/66499494-db429780-eab7-11e9-84c3-03a69511cd8a.PNG)

![Chat Room Create Output](https://user-images.githubusercontent.com/18084644/66499590-04632800-eab8-11e9-9281-dd8e5550b2b7.PNG)

![ChatRoom in OpenFire](https://user-images.githubusercontent.com/18084644/66499738-4b511d80-eab8-11e9-8e51-0af94f8ba874.PNG)

### Start monitoring messages in the sandbox
In the other service instance (let us call it "Chat Room Monitor", click on the "Monitor Chat Room" command. This command will never terminate so simply leave it running. The purpose of this command is to ensure that any messages entered into the chat room outside of the CloudShell GUI are reflected in the Output window in order to keep all permitted users of the sandbox up-to-date. This code is based on the class MucBot in the driver code.

![Chat Room Monitor](https://user-images.githubusercontent.com/18084644/66500258-1e513a80-eab9-11e9-8f94-f42312903ac7.PNG)

### Sending a chat room message from CloudShell
Sending a message to the sandbox users is simple. Click on the "Chat Room Service" service and click on the command "Send Chat Room Message".

![welcome msg](https://user-images.githubusercontent.com/18084644/66500532-99b2ec00-eab9-11e9-86aa-997bcde12e67.PNG)

![Send Message](https://user-images.githubusercontent.com/18084644/66500765-03cb9100-eaba-11e9-963c-c687d52ea306.PNG)

![Msg in Spark](https://user-images.githubusercontent.com/18084644/66500977-72a8ea00-eaba-11e9-9ba3-96299a62b1e7.PNG)

The message is echo'ed in CloudShell in the Output window, the monitor shows it again and you can see it directly in the Spark client for OpenFire.

### Seeing messages entered directly into OpenFire via a Client such as Spark

Let us imagine that someone finds it more convenient to send a message via a client app such as Spark. In this case, you will see the message automatically picked up and reflected in CloudShell.

![Msg Outside CS](https://user-images.githubusercontent.com/18084644/66501326-1c887680-eabb-11e9-9d36-83416d002ecd.PNG)

![Auto Monitor Message](https://user-images.githubusercontent.com/18084644/66501510-712bf180-eabb-11e9-8752-eced9d5329e2.PNG)

### Broadcast message

OpenFire offers a simple broadcast facility that displays a pop-up window to all users connected via Spark or some other IM client. An example is shown below.

![broadcast1](https://user-images.githubusercontent.com/18084644/66501987-5d34bf80-eabc-11e9-941e-7f4ae46f4747.PNG)

![broadcast1 5](https://user-images.githubusercontent.com/18084644/66502253-ce747280-eabc-11e9-8986-19d1c9a7dd2c.PNG)

![broadcast2](https://user-images.githubusercontent.com/18084644/66502142-9f5e0100-eabc-11e9-89f4-511e04b4da6c.PNG)

### Listing all chat room messages to-date

To get completely up-to-date with all the dialogue that has taken place in the sandbox chat room, simply click on the command "List Chat Room Message History". 

![ListMessageHistory0](https://user-images.githubusercontent.com/18084644/66503154-94a46b80-eabe-11e9-9879-a5843e362498.PNG)

![ListMessageHistory](https://user-images.githubusercontent.com/18084644/66502807-e7c9ee80-eabd-11e9-8fc6-62515ff3539d.PNG)

### Attach chat room message history

To display and attach a simple text file of the message history to the sandbox, simply click on the command "Attach Chat Room Message History". 

![attach0](https://user-images.githubusercontent.com/18084644/66503340-f1a02180-eabe-11e9-8622-183ddf417379.PNG)

![Attach1](https://user-images.githubusercontent.com/18084644/66503356-fa90f300-eabe-11e9-8973-f765d12dc18b.PNG)


## Suggested Improvements
1. If the sandbox name or any of its permitted users change, these are not automatically updated in the respective OpenFire chat room. An option to auto reflect such changes after a change should be offered perhaps.

2. Enhance the broadcast message command to reflect the message in all sandbox output windows not just the one the sender sent it from.
