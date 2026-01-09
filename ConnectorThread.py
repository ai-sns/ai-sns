import time
from PyQt6.QtCore import QSettings, QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from jabber import STATUS
import xmpp
import sys

import slixmpp
import asyncio
import sys
from db.DBFactory import query_AIFriend,update_AIFriend,add_AIFriend
import platform

class MyXMPPClient(slixmpp.ClientXMPP):

    def __init__(self, jid, password, con):
        super().__init__(jid, password)
        self.con = con
        self.jid = jid
        self.add_event_handler("session_start", self.on_session_start)
        self.add_event_handler("presence_subscribe", self.presence_subscribe)
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        # 设置心跳间隔（以秒为单位）
        self.heartbeat_interval = 3
        self.heartbeat_task = None
        # 注册roster更新事件处理器
        self.add_event_handler("roster_update", self.roster_update)
        self.rosternames = []
        self.con = con

    async def presence_subscribe(self, presence):
        # 获取订阅请求的 JID

        from_jid = presence['from']
        request_msg=presence['status']

        self.con.friend_subscribe_request.emit(f"{from_jid}",request_msg)


        # 接受订阅请求
        # self.send_presence(pto=from_jid, ptype='subscribed')
        # self.send_presence(pto=from_jid, ptype='subscribe')
        # print(f"Accepted subscription request from: {from_jid}")

        # 如果需要拒绝订阅请求，可以使用下面的代码而不是上面的接受代码
        # self.send_presence(pto=from_jid, ptype='unsubscribed')
        # print(f"Refused subscription request from: {from_jid}")


    def sendmessage(self, tojid, msg):
        self.send_presence()
        self.send_message(
            mto=tojid,
            mbody=msg,
            mtype='chat'
        )

    async def on_session_start(self, event):
        self.send_presence()
        await self.get_roster()
        # 启动心跳任务--开关
        self.heartbeat_task = asyncio.create_task(self.heartbeat())


    def roster_update(self, event):

        groups = self.client_roster.groups()
        rosters = self.client_roster
        rosternames = list(self.client_roster.keys())
        self.rosternames = rosternames
        for group in groups:
            for jid in groups[group]:
                self.update_roster_local(jid)
                # status = "Online" if self.client_roster[jid]['presence'] else "Offline"
        self.con.connected.emit()

    def update_roster_local(self,jid):
        if jid != self.jid:
            owner_sns_account = self.jid
            roster_data= self.client_roster[jid]
            account = jid
            nick_name = roster_data["name"]
            groups = ','.join(roster_data["groups"])
            record = query_AIFriend(account=account,owner_sns_account=self.jid)
            subscription = roster_data["subscription"]
            if record:
                update_AIFriend(record.id,owner_sns_account,nick_name=nick_name,groups=groups,subscription=subscription)
            else:
                memo =""
                sign=""
                name=""
                borndate="1900-01-01"
                gender=-1
                area=""
                city=""
                address=""
                mail=""
                phone=""
                organization=""
                title=""
                position=""
                add_AIFriend(account, nick_name, groups, owner_sns_account, memo, sign, subscription, name, borndate, gender, area, city, address, mail, phone, organization, title, position)

    def isConnected(self):
        return self.is_connected()

    def isConnecting(self):
        return self.is_connecting()

    async def heartbeat(self):
        while True:
            # 发送 Ping 消息到服务器
            try:
                await self['xep_0199'].ping()
            except Exception as e:
                print(f"Failed to ping server: {e}")
            # 等待指定的心跳间隔
            await asyncio.sleep(self.heartbeat_interval)

    def stop_heartbeat(self):
        if self.heartbeat_task is not None:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None


class ConnectorThread(QThread):
    connected = pyqtSignal()
    error = pyqtSignal(str, str)
    debug = pyqtSignal(str)
    message = pyqtSignal(object)
    presence = pyqtSignal(str, str, str)
    presence = pyqtSignal()
    subscriptionRequest = pyqtSignal(object)
    addBuddySig = pyqtSignal()
    rosterChange = pyqtSignal(object)
    connectSignal = pyqtSignal()
    friend_subscribe_request = pyqtSignal(str,str)

    def __init__(self, status,jid,password):
        super(ConnectorThread, self).__init__()
        self.status = status
        self.jid = jid
        self.password = password
        self.xmpp=None

    def set_jid(self,jid):
        self.jid=jid

    def set_password(self,password):
        self.password=password


    def run(self):

        # if  self.connect():#xmpp模式
        if self.connectslixmpp():
            self.Terminated = False
            # self.connected.emit()
            self.connect()
        else:

            self.Terminated = False
            # self.connected.emit()
            # self.connect()

        self.jabber.process(forever=False)  # slixmmp


    def connect(self):
        IP = self.jid.split('@')[1]
        PORT = 5222
        from_user = self.jid.split('@')[0]
        password = self.password
        client = xmpp.Client(IP)  # 是否开启debug
        self.jabber_xmpp = client

        client.connect(server=(IP, PORT))

        client.auth(from_user, password)

        client.sendInitPresence()


    def connectslixmpp(self):
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.set_event_loop(asyncio.new_event_loop())  # 需要创建一个loop，否则跑不起来，会报没有loop

        jid = self.jid
        password = self.password
        client = MyXMPPClient(jid, password, self)
        self.jabber = client
        client.connect()
        self.Terminated = False
        # self.connected.emit()
        # client.process(forever=True)
        asyncio.sleep(1)
        client.add_event_handler("message", self.xmpp_message)

    def disconnect(self):

        self.Terminated = True
        if self.jabber.isConnected():
            self.jabber.disconnect()

    def register_handlers(self):
        self.jabber.RegisterHandler('message', self.xmpp_message)
        self.jabber.RegisterHandler("iq", self.handle_version, typ="get", ns=xmpp.NS_VERSION)
        self.jabber.RegisterHandler("iq", self.handle_disco_info, typ="get", ns=xmpp.NS_DISCO_INFO)
        self.jabber.RegisterHandler("iq", self.rosterChange, typ="set", ns=xmpp.NS_ROSTER)
        self.jabber.RegisterHandler("presence", self.subscriptionRequest, typ="subscribe")
        self.jabber.RegisterHandler("presence", self.addBuddy, typ="subscribed")
        self.jabber.RegisterHandler("presence", self.presence)
        self.jabber.RegisterHandler("iq", self.request)
        self.jabber.RegisterDisconnectHandler(lambda: self.connectSignal.emit())

    def request(self, con, packet):
        self.debug.emit(str(packet) + "\n\n")

    def xmpp_message(self, msg):
        print("xmpp message received.")
        if msg['type'] in ('chat', 'normal'):
            body_content = msg['body']
            if body_content:
                self.message.emit(msg)

    def send_message_xmpp(self, tojid, message):
        m = xmpp.protocol.Message(to=tojid, body=message, typ='chat')
        self.debug.emit(str(m) + "\n\n")
        self.jabber_xmpp.send(m)

    def send_message(self, tojid, message):
        self.jabber.send_message(
            mto=tojid,
            mbody=message,
            mtype='chat'
        )


    def changeStatus(self, showId, status):
        p = xmpp.protocol.Presence()
        p.setShow(STATUS[showId])
        if status:
            p.setStatus(status)
        if showId == STATUS.available:
            p.setPriority(5)
        self.jabber.send(p)
        self.debug.emit(str(p) + "\n\n")

    def handle_version(self, con, iq):
        self.debug.emit(str(iq) + "\n")
        reply = iq.buildReply('result')
        reply.T.query.addChild(name="name", payload="AI-SNS")
        reply.T.query.addChild(name="version", payload="V1.0.0")
        if platform.mac_ver()[0]:
            plateforme = "Mac OS %s" % platform.mac_ver()[0]
        elif platform.win32_ver()[0]:
            plateforme = "Windows %s" % platform.win32_ver()[0]
        else:
            plateforme = "%s %s" % (platform.uname()[0], platform.uname()[2])
        reply.T.query.addChild(name="os", payload=plateforme)
        self.debug.emit(str(reply) + "\n")
        self.jabber.send(reply)

    def handle_disco_info(self, con, iq):
        self.debug.emit(str(iq) + "\n")
        reply = iq.buildReply('result')
        reply.T.query.addChild(name="feature", attrs={'var': 'jabber:iq:version'})
        self.debug.emit(str(reply) + "\n")
        self.jabber.send(reply)


    def getRoster_xmpp(self):
        self.roster = self.jabber.getRoster()
        return self.roster.getItems()

    def getRoster(self):
        rosternames = self.jabber.rosternames
        return rosternames

    def getGroups_xmpp(self, jid):
         return self.roster.getGroups(jid) if self.roster.getGroups(jid) else ['Buddies']

    def getGroups(self, jid):
        return self.jabber.client_roster[jid]['groups'] if self.jabber.client_roster[jid]['groups'] else ['Buddies']

    def getName(self, jid):
        # return self.roster.getName(jid)#xmpp
        return self.jabber.client_roster[jid]['name']

    def getStatus(self, jid):
        pass

    def presence(self, con, presence):
        self.debug.emit(str(presence) + "\n")
        jid = presence.getFrom().getStripped()
        if presence.getType() == "unavailable":
            self.presence.emit(jid, str(STATUS.unavailable))
        if not presence.getType():
            if not presence.getShow():
                self.presence.emit(jid, str(STATUS.available), presence.getStatus())
            else:
                status = presence.getShow()
                if status == "chat":
                    stat = STATUS.chat
                elif status == "dnd":
                    stat = STATUS.dnd
                elif status == "away":
                    stat = STATUS.away
                elif status == "xa":
                    stat = STATUS.xa
                else:
                    stat = STATUS.available
                self.presence.emit(jid, stat, presence.getStatus())

    def subscriptionRequest(self, con, presence):
        self.debug.emit(str(presence) + "\n")
        self.subscriptionRequest.emit(presence)

    def addBuddy(self, con, presence):
        self.debug.emit(str(presence) + "\n")
        self.addBuddySig.emit(presence)

    def rosterChange(self, con, iq):
        self.rosterChange.emit(iq)

    def isConnected(self):
        # return False

        if self.jabber:
            return self.jabber.isConnected()
        else:
            return False

    def accept_subscription(self,jid):
        # 接受订阅请求
        self.jabber.send_presence(pto=jid, ptype='subscribed')
        self.jabber.send_presence(pto=jid, ptype='subscribe')

        # 如果需要拒绝订阅请求，可以使用下面的代码而不是上面的接受代码
        # self.send_presence(pto=from_jid, ptype='unsubscribed')
        # print(f"Refused subscription request from: {from_jid}")

    def reject_subscription(self, jid):
        # 接受订阅请求
        self.jabber.send_presence(pto=jid, ptype='unsubscribed')
        self.jabber.send_presence(pto=jid, ptype='unsubscribe')
