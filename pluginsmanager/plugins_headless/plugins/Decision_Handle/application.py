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
        return_type = kwargs.get("return_type", "")
        answer = self.question + "from plugin"
        answer = self.question

        return (self.question,answer)

    def get_search_result(self, question):
        """
        Fetch the search results from the API based on the provided question.

        Args:
            question (str): The query string to send to the search API.

        Returns:
            str: The JSON string representation of the response from the API,
                 or an error message if the request fails.
        """
        config = self.get_config()  # Get configuration settings
        url = config.get("url", "https://api.tavily.com/search")  # API endpoint
        api_key = config.get("api_key", "")  # API key for authorization

        headers = {
            "Content-Type": "application/json",  # Specify request payload type
            "Authorization": f"Bearer {api_key}"  # Bearer token for authorization
        }

        data = {
            "query": question  # The query to be searched
        }

        # Send POST request to the API
        response = requests.post(url, headers=headers, json=data)

        # Check response status code for successful request
        if response.status_code != 200:
            error_message = f"Error: {response.status_code} - {response.text}"
            print(error_message)  # Log error message
            return error_message  # Return the error message as a string

        # Attempt to extract and return the JSON response as a string
        try:
            data = response.json()  # Parse JSON response
            results=data.get('results', [])
            print("results",results)
            return results
        except ValueError:
            print("Error: Failed to parse JSON response.")
            return "Error: Failed to parse JSON response."

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
