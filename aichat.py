import re

from openai import OpenAI
import time
import SparkApi


class AI_kimi:
    def __init__(self, temperature=0.3):
        self.api_key = "sk-LpAw4Go0TCRY7ZGRGWwpxU2c1C5uAVy0N3jN9M4XLg0ZkhOq"
        self.client = self.create_client(self.api_key)
        self.messages = {"role": "system", "content": "你是Kimi，由Moonshot AI提供的人工智能助手..."}
        self.model = "moonshot-v1-128k"
        self.temperature = temperature

    def create_client(self, api_key):
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )
        return client

    def get_client(self):
        return self.client

    # 发送对话请求
    def ask(self, questions):
        messages = []
        answers = []
        for q in questions:
            messages = []
            messages.append(self.messages)
            messages.append({"role": "user", "content": q})
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,  # 使用Kimi的模型
                    messages=messages,
                    temperature=self.temperature,  # 控制生成内容的随机性
                )
                # 打印Kimi的回答

                answer = (completion.choices[0].message.content)

                answers.append(completion.choices[0].message.content)
                print({"q": q, "a": answer})
            except Exception as e:
                print(str(e))
            time.sleep(0.5)
        # print(answer)
        return (answers)


class AI_spark:
    def __init__(self):
        self.appid = 'f2b807e2'
        self.api_key = "df1c1e0a354053264f400b2ebf85d5cf"
        self.api_secret = "YzIyM2Y0MTMyZjViMGNhZjdkMDkxZGI5"
        self.domain = "generalv3.5"  # v3版本
        self.Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3环境的地址（"wss://spark-api.xf-yun.com/v3.1/chat）
        self.text = []

    def getText(self, role, content):
        jsoncon = {}
        jsoncon["role"] = role
        jsoncon["content"] = content
        self.text.append(jsoncon)
        return self.text

    def getlength(self, text):
        length = 0
        for content in text:
            temp = content["content"]
            leng = len(temp)
            length += leng
        return length

    def checklen(self, text):
        while (self.getlength(text) > 8000):
            del text[0]
        return text

    def ask(self, questions):
        answers = []
        for q in questions:
            question = self.checklen(self.getText("user", q))
            SparkApi.answer = ""
            SparkApi.main(self.appid, self.api_key, self.api_secret, self.Spark_url, self.domain, question)
            print("-->", SparkApi.answer)
            ass = self.getText("assistant", SparkApi.answer)
            answers.append(SparkApi.answer)
        return answers

    def ask_one(self, q):
        answers = []
        question = self.checklen(self.getText("user", q))
        SparkApi.answer = ""
        SparkApi.main(self.appid, self.api_key, self.api_secret, self.Spark_url, self.domain, question)
        print("-->", SparkApi.answer)
        # ass = self.getText("assistant", SparkApi.answer)
        ass = SparkApi.answer
        questions = ass.strip().split('\n')
        # 遍历每个问题，进一步拆分内容
        for question in questions:
            # 移除每个问题前的编号和“问题：”字样
            # content = question.replace('问题：', '').strip()
            content = re.sub(r'^\d+\.\s*问题：\s*', '', question)
            # 将拆分后的内容添加到列表中
            answers.append(content)

        return answers
