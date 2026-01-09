import os
import os
import sys
import openai
import yaml
from logging import Logger

from pluginsmanager.engine import PluginCore
from pluginsmanager.model import Meta, Device
from logging import Logger
import json
import requests

from util import generate_random_id, download_image
from .OpenAIConnectionDialog import OpenAIConnectionDialog
from urllib.parse import urlencode
sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")
sys.path.append("../../../..")
sys.path.append("../../../../..")
from db.DBFactory import query_PluginMng


class Main():
    def __init__(self, record):
        id = record.id
        self.record = query_PluginMng(id=id)

    def open_config_dialog(self):
        connection = OpenAIConnectionDialog(self)
        connection.exec()

    def run(self, *args, **kwargs):
        self.question = args[0]
        return_type = kwargs.get("return_type","")

        results = self.google_custom_search(self.question)


        if return_type == "json":
            answer = results
        else:
            answer = f"以下是我通过ai搜索接口获得的结果，请你给我把json格式转换成更加容易阅读的普通模式。要求：1.不要以json或者其他结构化的方式输出。2.直接输出结果不要做其他任何说明。\n{json.dumps(results,ensure_ascii=False)}"
        return (self.question,answer)

    def google_custom_search(self, query, num_results=10,hl='zh-CN'):
        """
        使用Google Custom Search API检索并解析搜索结果。
        结果突出显示标题、URL和简要摘要，便于阅读和后续处理。

        :param api_key: Google API 密钥
        :param cx: Custom Search Engine ID
        :param query: 搜索关键词
        :param num_results: 返回结果数（最大为10）
        :return: 列表，每项为一个字典，包括title、link和snippet
        """
        config = self.get_config()  # Get configuration settings
        url = config.get("url", "https://www.googleapis.com/customsearch/v1")  # API endpoint
        api_key = config.get("api_key", "")  # API key for authorization
        cx = config.get("cx", "")  # API key for authorization

        # 构造查询参数，确保API调用简洁
        params = {
            'key': api_key,
            'cx': cx,
            'q': query,
            'num': min(max(num_results, 1), 10),  # API最大支持10
            'hl': hl,  # 可选：设置中文更便于理解
        }
        url = f'{url}?{urlencode(params)}'

        try:
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            # 捕获异常，有助于定位问题
            print(f"Google搜索API调用失败：{e}")
            return []

        results = []
        for item in data.get('items', []):
            # 只取重点字段：标题、URL、摘要
            results.append({
                "title": item.get('title', '').strip(),
                "url": item.get('link', '').strip(),
                "content": item.get('snippet', '').replace('\n', '').strip()
            })
        print("results", results)
        return results

    def get_config(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            pass

        return config


class Connector_OpenAI_Plugin(PluginCore):

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)
        self.meta = Meta(
            name='Tavily',
            description='用来进行AI搜索',
            version='1.0.0'
        )
        print("init meta", self.meta)
        self.type = "Tool_Headless"
        self.connection_mode = "OpenAI"

    def get_config(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
            with open(file_path, "r") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            pass

        return config

    def set_config(self, new_config):
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
            with open(file_path, "w") as f:
                yaml.safe_dump(new_config, f)
        except Exception as e:
            print(f"Error while saving YAML file: {e}")

    def invoke(self, command) -> str:
        api_key = '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'
        stream = True
        connection = OpenAIConnectionDialog(self)
        content = ""

        if command[0] == "open_config_dialog":
            print("opendialogue")
            connection.exec()
        else:
            headers = {
                'Authorization': f'Bearer {api_key}',
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": command,
                "max_tokens": 4000,
                "temperature": 0.9,
                "top_p": 1.0,
                "n": 1,
                "stop": None,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.6,
                "stream": stream
            }

            try:
                api_url = "https://api.openai.com/v1/chat/completions"
                # response = requests.post(api_url, json=body, headers=headers, stream=stream)
                response = requests.post(api_url, headers=headers, data=json.dumps(data), stream=stream)

                if not stream:
                    response_json = response.json()
                    print("response_json:", response_json)
                    return ''.join([choice['message']['content'] for choice in response_json['choices']])

                def generator():
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data: ") and decoded_line.strip() != "data: [DONE]":
                                try:
                                    chunk = json.loads(decoded_line[6:])
                                    if 'choices' in chunk and len(chunk['choices']) > 0:
                                        chunk_message = chunk['choices'][0].get('delta', {}).get('content', '')
                                        if chunk_message:
                                            print("chunk_message:", chunk_message)
                                            yield chunk_message
                                except json.JSONDecodeError:
                                    continue

                return generator()

            except Exception as e:
                print(f"Openai连接失败: {e}")
                return "Openai连接失败"

        return content
