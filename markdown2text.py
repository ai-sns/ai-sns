import re


def markdown_to_plain_text(markdown_text):
    """
    将Markdown格式的文本转换为纯文本，去除Markdown符号。

    参数:
    markdown_text (str): Markdown格式的字符串。

    返回:
    str: 仅包含内容的纯文本字符串。
    """

    # 去除标题符号 #
    text = re.sub(r'^#+\s*', '', markdown_text, flags=re.MULTILINE)

    # 去除列表符号 - 和 *
    text = re.sub(r'^[\*\-]\s+', '', text, flags=re.MULTILINE)

    # 去除加粗和斜体符号 **, __, *, _
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # 加粗
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)  # 斜体

    # 去除链接格式 [text](url)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# 示例测试
if __name__ == "__main__":
    markdown_sample = """
    # 标题
    这是一个**Markdown**文本示例。

    - 列表项1
    - 列表项2

    [链接](http://example.com)
    """

    plain_text = markdown_to_plain_text(markdown_sample)
    print(plain_text)
