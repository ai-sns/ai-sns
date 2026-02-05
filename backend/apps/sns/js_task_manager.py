from util import generate_random_id
from db.DBFactory import add_map_activity,query_map_activity_previous,query_AiChatCfg_map_setting,query_AIChatMessages_All_previous
import json

class JsTaskManager:
    def __init__(self,parent):
        # 初始化一个字典和几个列表
        self.parent = parent

    def show_information(self,info,type_str="1"):
        command = ("show_information", info, "")
        self.parent.send_msg_to_map(command)
        activity_id = generate_random_id()
        content = info
        add_map_activity(activity_id, content, type_str)




