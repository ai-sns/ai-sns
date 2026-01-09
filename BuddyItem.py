import datetime

from PyQt6.QtWidgets import QTreeWidgetItem, QApplication, QDialog, QVBoxLayout, QMenu,QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt,  QSettings

from MessageBox import MessageBox
from AddBuddyDialog import AddBuddyDialog

from jabber import STATUS
from jabber import STATUS_IMAGE
from db.DBFactory import add_AIChatMessages,update_AIFriend
from util import generate_random_id,get_aifriend_msg_title_formatted,add_msg_to_message_windowv2,add_msg_to_message_window_with_markdown_and_highlightv2
class BuddyItem(QTreeWidgetItem):
    """
      BuddyItem implements the view of a Buddy from the Roster
    """



    def __init__(self, parent, jid, con, mainwindow,ai_chat_cfg,chat_type="0"):
        super(BuddyItem, self).__init__(parent, [jid], QTreeWidgetItem.ItemType.UserType + 1)


        # QTreeWidgetItem configuration
        self.setFlags(Qt.ItemFlag.ItemIsDragEnabled |  Qt.ItemFlag.ItemIsEnabled)  # we can move a contact
        self.parent = parent
        self.jid = jid
        self.name = jid
        self.setStatus(STATUS.unavailable)
        self.connectionThread = con
        self.mainwindow = mainwindow
        self.ai_chat_cfg = ai_chat_cfg
        self.is_browser_page_loaded = False
        self.chat_type = chat_type  # chat_type 0是普通聊天，1是地图聊天
        self.main_chat_widget = None
        self.message_box = None
        # self.setObjectName(jid)

    def setStatus(self, status):
        self.status = status
        if self.status not in range(6):
            self.status = STATUS.unavailable


    def setName(self, name):
        if name:
            self.name = name
            self.setText(0, name)

    def getStatus(self):
        return self.status

    def isAway(self):
        return (self.status == STATUS.away or self.status == STATUS.xa)

    def isOffline(self):
        if self.status == STATUS.unavailable:
            return True
        else:
            return False

    def open_chat_window(self, is_received_message=False):
        print("in createDialog")

        if self.chat_type == "1":
            if not self.main_chat_widget:
                self.main_chat_widget = self.mainwindow.map_window_widget
                self.main_chat_widget.setWindowIcon(QIcon("images/mail.png"))

                self.message_box = self.mainwindow.map_message_box
                layout = QVBoxLayout(self.main_chat_widget)
                layout.addWidget(self.message_box)
                self.main_chat_widget.setLayout(layout)
                self.main_chat_widget.setWindowTitle(self.main_chat_widget.tr("Chat with ") + self.name)

        else:
            if not self.main_chat_widget:
                self.main_chat_widget = QWidget()
                self.main_chat_widget.setWindowIcon(QIcon("images/mail.png"))

                self.message_box = MessageBox(self.main_chat_widget, self.connectionThread, self.jid, self.name, self.ai_chat_cfg, self)
                layout = QVBoxLayout(self.main_chat_widget)
                layout.addWidget(self.message_box)
                self.main_chat_widget.setLayout(layout)
                self.main_chat_widget.setWindowTitle(self.main_chat_widget.tr("Chat with ") + self.name)




            # 获取QStackedWidget中所有widget
            total_widgets = self.mainwindow.stack_main_widget.count()

            # 检查dialog是否已添加
            is_added = False
            for i in range(total_widgets):
                if self.mainwindow.stack_main_widget.widget(i) is self.main_chat_widget:
                    is_added = True
                    break

            # 检查是否为当前显示的widget
            is_current = (self.mainwindow.stack_main_widget.currentWidget() is self.main_chat_widget)

            if not is_added:
                self.mainwindow.stack_main_widget.addWidget(self.main_chat_widget)

            if not is_current:
                if is_received_message:
                    red_icon = QIcon('images/redpoint.png')
                    self.setIcon(0, red_icon)
                    account = self.jid
                    owner_sns_account = self.ai_chat_cfg.account
                    update_time = datetime.datetime.now()
                    update_AIFriend(account, owner_sns_account, last_message_time=update_time, new_message_flag=True)


                else:
                    self.mainwindow.stack_main_widget.setCurrentWidget(self.main_chat_widget)


        self.set_top(is_received_message)




        print("goingaddconver3")

    def receiveMessage(self, event):
        self.open_chat_window(is_received_message=True)
        # self.msg.receiveMessage(event)

        browser_page = self.message_box.messageBrowser.page()
        browser_page.loadFinished.connect(self.onLoadFinished)  # 第一次可能page没来得及load，所以需要在onload中处理
        self.message_box.first_event = event

        self.browser_page = browser_page
        self.msg_event = event

        if self.message_box.is_browser_page_loaded == True:  # page是否已经load了
            self.is_browser_page_loaded = True

        if self.is_browser_page_loaded == True:
            self.onLoadFinished(True)

    def onLoadFinished(self, success):
        if success:
            browser_page = self.browser_page
            event = self.msg_event
            self.message_box.receiveMessage(event)
            self.is_browser_page_loaded = True


            if not event is None:

                self.message_box.increment_page_index()
                page_index = self.message_box.page_index

                friend_msg_title = get_aifriend_msg_title_formatted(page_index,self.name)
                add_msg_to_message_windowv2(browser_page, friend_msg_title, 1)

                add_msg_to_message_window_with_markdown_and_highlightv2(browser_page, event['body'], 2)



            if not self.message_box.conversation_id:
                conversation_id = generate_random_id()
                self.message_box.conversation_id = conversation_id
                is_first = True
            else:
                is_first = False


            add_AIChatMessages(self.message_box.conversation_id, 1, event['body'], event['body'], self.ai_chat_cfg.name, self.ai_chat_cfg.account, self.name, self.jid, is_first)


            # if self.msg.first_reply:
            #     message = f"""<strong><span style="color: darkblue; font-size:14pt;">buddyitem用户 :</span></strong><br> {self.msg.first_reply}<br>"""
            #
            #     browser_page.runJavaScript('document.getElementById("allcontent").innerHTML +=`' + message + '`')
            #
            #     add_AIChatMessages( self.msg.conversation_id, 0, event['body'], self.msg.first_reply, self.ai_chat_cfg.name, self.ai_chat_cfg.account, self.name, self.jid, False)
            #
            #     self.msg.first_reply = ""

            browser_page.runJavaScript("window.scrollTo(0, document.body.scrollHeight);")

    def sendMessageByAgent(self, content):
        self.open_chat_window()
        self.message_box.sendMessage(content)

    def set_top(self,is_received_message=False):
        buddyList = self.mainwindow.buddylist_list[self.ai_chat_cfg.user_id]


        parent = self.parent
        if parent:
            # 从父项目中移除当前项目
            parent.removeChild(self)
            # 将项目插入到父项目的第一个位置

            parent.insertChild(0, self)

        account = self.jid
        owner_sns_account = self.ai_chat_cfg.account
        update_time = datetime.datetime.now()

        update_AIFriend(account,owner_sns_account,last_message_time=update_time)

        top_level_item = buddyList.topLevelItem(0)
        # 选定第一个子项
        if top_level_item.childCount() > 0:
            top_level_item.child(1).setSelected(True)

        if not is_received_message:
            # 清空选定项
            buddyList.clearSelection()
            self.setSelected(True)
            buddyList.setCurrentItem(self)





    def __str__(self):
        return u'%s' % self.name


