from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QHeaderView, QTreeWidgetItemIterator
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtCore import Qt, QPoint
from db.DBFactory import query_AIChatMessages_All
from BuddyItemMap import BuddyItem
from BuddyGroup import BuddyGroup
from PyQt6.QtCore import QSettings, QThread, pyqtSignal
import time
from i18n import lt



from db.DBFactory import query_AiChatCfg_Search_Content,query_AIFriend


class BuddyList(QTreeWidget):
    """BuddyList implements the view in a Tree of the Roster"""
    rename_signal = pyqtSignal(object)
    def __init__(self, parent,ai_chat_cfg,chat_type="0"):
        print("cjrok in buddy list")

        super(BuddyList, self).__init__(parent)
        print("buddylist parent",parent)
        self.connection = None
        self.mainwindow=parent
        self.ai_chat_cfg = ai_chat_cfg
        self.chat_type = chat_type#chat_type 0是普通聊天，1是地图聊天
        # self.messagebox = self.mainwindow.map_message_box

        #
        #
        # # 添加顶层项
        top_item = QTreeWidgetItem(self)
        top_item.setText(0, lt("Not login yet","尚未登录"))
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
        self.setHeaderLabel(lt("Contact List","联系人列表"))#需要设置此处的值，否则缺省值为1
        # self.setSortingEnabled(True)#不要设置这个值否则影响排序，影响顺序，会自动按字母排序
        # self.sortItems(0, Qt.SortOrder.AscendingOrder)#不要设置这个值否则影响排序，影响顺序，会自动按字母排序
        self.buddies = {}
        self.groups = {}
        self.tree = {}

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.menu = QMenu()
        self.rename_action = QAction(QIcon("images/rename.png"), "重命名", self)
        self.rename_action.triggered.connect(self.rename)
        self.menu.addAction(self.rename_action)
        self.menu.addAction(QIcon("images/namecard.png"), "用户信息", self.getInfo)

        self.customContextMenuRequested.connect(self.context)

        self.offline = True
        self.away = False
        self.current_chat_item = None
        self.itemDoubleClicked.connect(self.on_itemDoubleClicked)

    def re_init(self):
        self.connection = None
        top_item = QTreeWidgetItem(self)
        top_item.setText(0, "尚未登录")


        self.buddies = {}
        self.groups = {}
        self.tree = {}
        self.current_chat_item = None
        # self.mainwindow.show_ai_home()


    def on_itemDoubleClicked(self, item, column):

        print("双击了：", item.text(column))
        print(column)

        if not hasattr(item, "jid"):
            return

        id_value = item.jid
        print("双击了：", id_value)


        if id_value == None:
            return (False)

        friend_account = id_value

        self.messagebox = self.mainwindow.map_message_box
        self.messagebox.taskmng_js.clear_chat_list()

        owner_account = self.ai_chat_cfg.account
        records = query_AIChatMessages_All(owner_account=owner_account,friend_account=friend_account)
        if records:
            for record in records:
                content = record.content
                friend_name = record.friend_name
                if record.flag == 0:
                    content = f"[MyAi]:{content}<br><br>{record.create_time.strftime('%Y-%m-%d %H:%M:%S')}"
                else:
                    content = f"[{friend_name}]:{content}<br><br>{record.create_time.strftime('%Y-%m-%d %H:%M:%S')}"

                self.messagebox.taskmng_js.show_information_chat_list(content)
                self.messagebox.taskmng_js.last_record_id_chat = record.id
                self.messagebox.taskmng_js.last_friend_account = record.friend_account


        # records = query_AgentTask_Content(id=id_value)
        # agent = self.agent
        # agentcfg = self.agent_cfg
        #
        # self.mainwindow.open_agent_task_chat(agent)
        # agent_chat_window = self.mainwindow.agent_chat_window_list[agentcfg.user_id]
        # taskpage = agent_chat_window.findChild(TaskPage, "TaskPageObject")
        # self.taskpage = taskpage
        #
        # task_id = ""
        # if records:
        #     task_id = records[0].task_id
        #     for record in records:
        #         problem = self.get_record_problem_for_message(record)
        #         question_div_id = "id_" + str(record.id) + "_a"
        #         answer_div_id = "id_" + str(record.id) + "_r"
        #         taskpage.messages_mng.append_message(question_div_id,{"role":
        #                                                            "user", "content": problem})
        #         taskpage.messages_mng.append_message(answer_div_id,{"role": "assistant", "content": record.answer})
        #
        # taskpage.task_id = task_id
        # taskpage.is_first = False
        # browser_page = taskpage.messageBrowser.page()
        # browser_page.loadFinished.connect(self.onLoadFinished)  # 第一次可能page没来得及load，所以需要在onload中处理
        # self.browser_page = browser_page
        # self.tasks_history = records
        #
        # if taskpage.is_browser_page_loaded == True:  # page是否已经load了
        #     self.is_browser_page_loaded = True
        #
        # if self.is_browser_page_loaded == True:
        #     self.onLoadFinished(True)
        #
        # taskpage.messageEdit.setFocus()


    def setConnection(self, con):
        self.connection = con
        #一个buddylist对应一个用户的ConnectThread

    def addItem(self, jid):
        print("buddylist-->",self.__str__)
        if self.connection:

            item_count = self.topLevelItemCount()
            if item_count > 0:
                if self.topLevelItem(0).text(0)=='等待登录加载中...':
                    self.takeTopLevelItem(0)

            # group = self.connection.getGroups(jid)[0]#帐号所属的group列表中的第一个
            group = "Buddies"#统一指定这一个
            self.addGroup(group)
            if jid not in self.buddies.keys():
                self.buddies[jid] = BuddyItem(self.groups[group], jid, self.connection,self.mainwindow,self.ai_chat_cfg,self.chat_type)
                self.buddies[jid].setName(self.connection.getName(jid))
                self.set_item_status(self.buddies[jid])
                print("cjr in load itemthe jid:",jid)
                # self.buddies[jid].setObjectName(jid)
            self.groups[group].addChild(self.buddies[jid])
            self.tree[group][jid] = self.buddies[jid]
            print(self.groups)
            print(self.tree)


    def set_item_status(self,item):
        red_icon = QIcon('images/redpoint.png')
        account = item.jid
        owner_sns_account=self.ai_chat_cfg.account
        record = query_AIFriend(account=account,owner_sns_account=owner_sns_account)
        if record.new_message_flag:
            item.setIcon(0, red_icon)



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
            # self.buddies[buddy] = BuddyItem(None, buddy)

            group = "Buddies"  # 统一指定这一个
            self.addGroup(group)
            self.buddies[buddy] = BuddyItem(self.groups[group], buddy, self.connection,self.mainwindow,self.ai_chat_cfg,self.chat_type)

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
            if item.type() == QTreeWidgetItem.ItemType.UserType + 1:
                self.currentItem = item
                self.menu.popup(self.mapToGlobal(pos))

    def rename(self):
        self.rename_signal.emit(self.currentItem)

    def getInfo(self):
        pass

    def deselect_all_items(self):
        print("deselect all")
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            print("deselect one")
            iterator.value().setSelected(False)
            iterator += 1

