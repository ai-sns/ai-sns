from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction, QHeaderView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPoint

from BuddyItem import BuddyItem
from BuddyGroup import BuddyGroup
from PyQt5.QtCore import QSettings, QThread, pyqtSignal
import time

from db.DBFactory import query_AiChatCfg_Search_Content


class BuddyList(QTreeWidget):
    """BuddyList implements the view in a Tree of the Roster"""
    rename_signal = pyqtSignal(object)
    def __init__(self, parent,ai_chat_cfg):

        super(BuddyList, self).__init__(parent)
        print("buddylist parent",parent)
        self.connection = None
        self.mainwindow=parent
        self.ai_chat_cfg = ai_chat_cfg

        #
        #
        # # 添加顶层项
        top_item = QTreeWidgetItem(self)
        top_item.setText(0, "尚未登录")
        #
        # # 添加子项
        # child_item = QTreeWidgetItem(top_item)
        # child_item.setText(0, "Child Item")
        #
        # # 添加多个顶层项
        # for i in range(3):
        #     top_item = QTreeWidgetItem(self)
        #     top_item.setText(0, f"Top Level Item {i + 1}")
        #
        # self.expandAll()  # 展开所有项


        #QTreeWidgetItem configuration
        #self.header().setSectionHidden(0, True)
        self.setHeaderLabel("联系人列表")#需要设置此处的值，否则缺省值为1
        self.setSortingEnabled(True)
        self.sortItems(0, Qt.AscendingOrder)
        self.buddies = {}
        self.groups = {}
        self.tree = {}

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu = QMenu()
        self.rename_action = QAction(QIcon("images/rename.png"), "重命名", self)
        self.rename_action.triggered.connect(self.rename)
        self.menu.addAction(self.rename_action)
        self.menu.addAction(QIcon("images/namecard.png"), "用户信息", self.getInfo)

        self.customContextMenuRequested.connect(self.context)

        self.offline = True
        self.away = False

    def re_init(self):
        self.connection = None
        top_item = QTreeWidgetItem(self)
        top_item.setText(0, "尚未登录")

        self.buddies = {}
        self.groups = {}
        self.tree = {}



    def setConnection(self, con):
        self.connection = con
        #一个buddylist对应一个用户的ConnectThread

    def addItem(self, jid):
        if self.connection:

            item_count = self.topLevelItemCount()
            if item_count > 0:
                if self.topLevelItem(0).text(0)=='等待登录加载中...':
                    self.takeTopLevelItem(0)

            group = self.connection.getGroups(jid)[0]
            self.addGroup(group)
            if jid not in self.buddies.keys():
                self.buddies[jid] = BuddyItem(self.groups[group], jid, self.connection,self.mainwindow,self.ai_chat_cfg)
                self.buddies[jid].setName(self.connection.getName(jid))
                print("the jid:",jid)
                # self.buddies[jid].setObjectName(jid)
            self.groups[group].addChild(self.buddies[jid])
            self.tree[group][jid] = self.buddies[jid]

    def addGroup(self, group):
        if group:
            if group not in self.groups.keys():
                self.groups[group] = BuddyGroup(group)
                self.tree[group] = {}
                self.addTopLevelItem(self.groups[group])


    def setOffline(self, hide):
        self.offline = hide
        self.hideGroups()

    def setAway(self, hide):
        self.away = hide
        self.hideGroups()

    def hideGroups(self):
        for child in self.buddies.values():
            if child.isOffline():
                child.setHidden(self.offline)
            elif child.isAway():
                child.setHidden(self.away)
            else:
                child.setHidden(False)

        for group in self.tree.keys():
            hide = True
            for child in self.tree[group].values():
                if not child.isHidden():
                    hide = False
            self.groups[group].setHidden(hide)
        self.expandAll()

    def message(self, event):
        buddy = event['from']
        print("buddyfull",buddy.full)#yangyang@xabber.de/gajim.CZ6PGQG0
        print("buddyuser", buddy.user)
        print("buddylocal", buddy.local)
        print("buddyusername", buddy.username)
        print("buddydomain", buddy.domain)
        print("buddynode", buddy.node)
        print("buddybare", buddy.bare)#yangyang@xabber.de
        print("buddyresource", buddy.resource)#gajim.CZ6PGQG0
        buddy = buddy.bare
        if buddy not in self.buddies.keys():
            self.buddies[buddy] = BuddyItem(None, buddy)
        self.buddies[buddy].receiveMessage(event)



    def send_message(self, jid,content):

        self.buddies[jid].sendMessageByAgent(content)

    def presence(self, jid, status, show=None):
        if jid in self.buddies.keys():
            self.buddies[jid].setStatus(status)
        else:
            time.sleep(2.0)
            self.presence(jid, status, show)
        self.hideGroups()

    def context(self, pos):
        item = self.itemAt(pos)
        if item:
            if item.type() == QTreeWidgetItem.UserType + 1:
                self.currentItem = item
                self.menu.popup(self.mapToGlobal(pos))

    def rename(self):
        self.rename_signal.emit(self.currentItem)

    def getInfo(self):
        pass


    def search(self, key_word):
        print("buddylist searching", key_word)
        self.reload(key_word)

    def reload(self, key_word):
        self.clear()

        self.setHeaderLabel("联系人列表")  # 需要设置此处的值，否则缺省值为1  "对话列表"
        self.buddies = {}
        self.groups = {}
        self.tree = {}

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.menu = QMenu()
        self.rename_action = QAction(QIcon("images/rename.png"), "重命名", self)
        self.rename_action.triggered.connect(self.rename)
        self.menu.addAction(self.rename_action)

        # self.delete_action = QAction(QIcon("images/infos.png"), "删除", self)
        # self.delete_action.triggered.connect(self.delete_item)
        # self.menu.addAction(self.delete_action)

        self.customContextMenuRequested.connect(self.context)
        # self.itemDoubleClicked.connect(self.on_itemDoubleClicked)

        if key_word.startswith('+++'):
            # 获取上一次的搜索结果并过滤
            filtered_tasklist = [
                record for record in self.tasklist
                if key_word[3:] in record.title or key_word[3:] in record.problem or key_word[3:] in record.answer
            ]
        else:
            # self.tasklist = query_AgentTask_Search_Content(
            #     agent_id=self.agent_cfg.user_id, title=key_word, problem=key_word, answer=key_word
            # )
            # self.tasklist = query_AgentTaskMulti(is_first=True, group_id=self.agentcfg.group_id,title=key_word)
            self.tasklist = query_AiChatCfg_Search_Content(nickname=key_word,
                                                             account=key_word
                                                                )

            filtered_tasklist = self.tasklist

        # 创建一个集合来存储已经处理过的 first_record 记录
        processed_first_records = set()

        for record in filtered_tasklist:

            self.addItem(record)
