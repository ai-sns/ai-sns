import os

from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_core.documents.base import Document
import json
os.environ['HUGGINGFACEHUB_API_TOKEN'] = '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'
# os.environ["OPENAI_API_KEY"] = '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'
os.environ["GOOGLE_CSE_ID"] = "53b9c3fd76d8d4cbb"
os.environ["GOOGLE_API_KEY"] = "AIzaSyAYEpRPu24tU41bFn4QQB_2cZFmlOZxEEE"
from langchain.document_loaders import DirectoryLoader, TextLoader,powerpoint,word_document,excel,PyPDFLoader,PyMuPDFLoader,markdown,html,web_base,AsyncChromiumLoader,csv_loader
# from langchain.chains import ConversationalRetrievalChain
# from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from util import image_to_base64
from pinecone import Pinecone
from db.DBFactory import query_KMCfg
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Union, Literal, Annotated
"""
 pip install chromadb==0.4.24
 pip install tiktoken
"""
#导入文档加载器
from langchain.document_loaders import DirectoryLoader, TextLoader

# Download the 'punkt' resource if it's not already available


from nltk.tokenize import sent_tokenize
from unstructured.partition.text_type import is_possible_narrative_text
# import nltk
# try:
#     nltk.data.find('tokenizers/punkt')
#     nltk.download('punkt')
#     nltk.download('punkt_tab')
#     nltk.download('all')
# except LookupError:
#     nltk.download('punkt')
#     nltk.download('punkt_tab')
#     nltk.download('all')
def savevector(filepath,persist_directory,embedding_model_name,emb_type="openai",chunk_size=500, chunk_overlap=20):

    #指定chroma持久化的目录，当我们不知道目录时,chroma会将数据存储在内存中，随着程序的关闭就会删除
    # persist_directory = "C:\\dev\\ai-sns\\PyTalk\\pytalk\\vector_store"
    #按目录加载文档
    # loader = DirectoryLoader('C:\\0资料\\12.Omniverse\\青田项目\\经商局\\km\\cleaned\\', glob='**/*.txt')
    # docs = loader.load()
    #加载单个文档 可以自由选择
    # loader = TextLoader(filepath, encoding='utf8')
    ext = os.path.splitext(filepath)[1].lower()  # 获取文件扩展名并转为小写
    loaders = {
        '.txt': lambda path: TextLoader(path, encoding='utf8'),
        '.js': lambda path: TextLoader(path, encoding='utf8'),
        '.sql': lambda path: TextLoader(path, encoding='utf8'),
        '.pdf': PyPDFLoader,
        '.docx': word_document.UnstructuredWordDocumentLoader,
        '.xls': excel.UnstructuredExcelLoader,
        '.xlsx': excel.UnstructuredExcelLoader,
        '.csv': csv_loader.UnstructuredCSVLoader,
        '.pptx': powerpoint.UnstructuredPowerPointLoader,
        '.md': markdown.UnstructuredMarkdownLoader,
        '.html': html.UnstructuredHTMLLoader,
        '.htm': html.UnstructuredHTMLLoader,
    }

    if ext in loaders:
        loader = loaders[ext](filepath)
        docs = loader.load()  # 数据转换

    file_name=os.path.basename(filepath)




    if emb_type == "openai":
        # 调用openai Embeddings  OPENAI_API_BASE
        # embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
        embeddings = OpenAIEmbeddings(openai_api_key="sk-SVCuk9EAqrgUEvvh31PKxVIr1fZhwt5boDB2Hexw8vs2Bl26",openai_api_base="https://api.chatanywhere.tech/v1/")
        # embedding_model_name = 'shibing624/text2vec-bge-large-chinese'
    else:
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)


    # 文档切块目的是为了防止超出GPTAPI的token限制 RecursiveCharacterTextSplitter,CharacterTextSplitter,TokenTextSplitter,CodeTextSplitter
    text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # text_splitter = RecursiveCharacterTextSplitter()
    # text_splitter = CharacterTextSplitter()
    doc_texts = text_splitter.split_documents(docs)
    for doc in doc_texts:
        print(doc)
        doc.metadata["source"]=file_name
    # 向量化
    vectordb = Chroma.from_documents(doc_texts, embeddings, persist_directory=persist_directory)
    # 持久化
    vectordb.persist()
    #执行到这里你会发现public目录下多了一些以parquest结尾的文件,这些文件就是chroma持久化本地的向量数据
    del embeddings


def savevector_pinecone(filepath,persist_directory,config,chunk_size=500, chunk_overlap=20):

    ext = os.path.splitext(filepath)[1].lower()  # 获取文件扩展名并转为小写
    loaders = {
        '.txt': lambda path: TextLoader(path, encoding='utf8'),
        '.js': lambda path: TextLoader(path, encoding='utf8'),
        '.sql': lambda path: TextLoader(path, encoding='utf8'),
        '.pdf': PyPDFLoader,
        '.docx': word_document.UnstructuredWordDocumentLoader,
        '.xls': excel.UnstructuredExcelLoader,
        '.xlsx': excel.UnstructuredExcelLoader,
        '.csv': csv_loader.UnstructuredCSVLoader,
        '.pptx': powerpoint.UnstructuredPowerPointLoader,
        '.md': markdown.UnstructuredMarkdownLoader,
        '.html': html.UnstructuredHTMLLoader,
        '.htm': html.UnstructuredHTMLLoader,
    }

    if ext in loaders:
        loader = loaders[ext](filepath)
        docs = loader.load()  # 数据转换

    file_name=os.path.basename(filepath)

    # 文档切块目的是为了防止超出GPTAPI的token限制 RecursiveCharacterTextSplitter,CharacterTextSplitter,TokenTextSplitter,CodeTextSplitter
    text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # text_splitter = RecursiveCharacterTextSplitter()
    # text_splitter = CharacterTextSplitter()
    doc_texts = text_splitter.split_documents(docs)
    for doc in doc_texts:
        print(doc)
        doc.metadata["source"]=file_name


    pc = Pinecone(api_key=config.get("api_key"))

    # Define index name
    index_name = config.get("index_name")

    # Check if the index already exists; if not, create it
    if not pc.has_index(index_name):
        pc.create_index_for_model(
            name=index_name,
            cloud=config.get("cloud"),
            region=config.get("region"),
            embed={
                "model": config.get("embed_model"),
                "field_map": config.get("embed_field_map")  # Mapping the 'text' field to 'chunk_text'
            }
        )

    # Instantiate the index to interact with it
    index = pc.Index(index_name)

    # Prepare records to be upserted into the index
    records = [
        {
            "_id": str(index + 1),  # 使用索引生成唯一的 id, 从 1 开始
            "source":doc.metadata["source"],
            "chunk_text": doc.page_content,  # 将每个文档的 page_content 作为 chunk_text
            "category": "auto"
        }
        for index, doc in enumerate(doc_texts)  # 使用 enumerate 获取索引和文档对象
    ]

    # Upsert records into the index; specify the namespace for organization
    index.upsert_records(namespace=config.get("namespace"), records=records)

    print(index.describe_index_stats())



def update_vector(filepath,persist_directory,embedding_model_name,emb_type="openai",chunk_size=500, chunk_overlap=20,vector_type=""):
    km_path = extract_km_path(persist_directory)
    km_record = query_KMCfg(kmpath=km_path)
    vector_type = km_record.vectortype

    if vector_type == "Pinecone":
        delete_vector_pinecone(filepath, persist_directory, embedding_model_name, emb_type)
        return

    if vector_type == "Pinecone":
        update_vector_pinecone(filepath,persist_directory,embedding_model_name,emb_type,chunk_size, chunk_overlap)
        return

    delete_vector(filepath, persist_directory, embedding_model_name, emb_type)
    savevector(filepath, persist_directory, embedding_model_name, emb_type, chunk_size, chunk_overlap)


def update_vector_pinecone(filepath,persist_directory,embedding_model_name,emb_type="openai",chunk_size=500, chunk_overlap=20):

    delete_vector_pinecone(filepath, persist_directory, embedding_model_name, emb_type)
    savevector_pinecone(filepath, persist_directory, embedding_model_name, emb_type, chunk_size, chunk_overlap)




def delete_vector(filepath,persist_directory,embedding_model_name,emb_type = "openai",vector_type=""):
    km_path = extract_km_path(persist_directory)
    km_record = query_KMCfg(kmpath=km_path)
    vector_type = km_record.vectortype


    if vector_type == "Pinecone":
        delete_vector_pinecone(filepath,persist_directory,embedding_model_name,emb_type)
        return
    file_name = os.path.basename(filepath)
    # if emb_type == "openai":
    #     # 调用openai Embeddings
    #     embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    #     # embedding_model_name = 'shibing624/text2vec-bge-large-chinese'
    # else:
    #     embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
    persist_directory = os.path.abspath(persist_directory)
    # vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    vectordb = Chroma(persist_directory=persist_directory)
    docs = vectordb.get(where={"source": file_name})
    if len(docs["ids"])>0:
        vectordb.delete(ids=docs["ids"])
    # del embeddings

def delete_vector_pinecone(filepath,persist_directory,embedding_model_name,emb_type):
    file_name = os.path.basename(filepath)
    km_path = extract_km_path(persist_directory)
    km_record = query_KMCfg(kmpath=km_path)
    config_param = km_record.config_param
    # 将JSON字符串解析为Python字典
    params = json.loads(config_param)

    # 提取各个参数
    config = {
        "api_key": params.get("api_key"),
        "cloud": params.get("cloud"),
        "region": params.get("region"),
        "index_name": params.get("index_name"),
        "namespace": params.get("namespace"),
        "top_k": params.get("top_k"),
        "embed_model": params["embed"].get("model"),
        "embed_field_map": params["embed"].get("field_map"),
        "rerank_model": params["rerank"].get("model"),
        "rerank_top_n": params["rerank"].get("top_n"),
        "rerank_fields": params["rerank"].get("rank_fields"),
        "fields": params.get("fields")
    }

    # Initialize Pinecone client with the provided API key
    pc = Pinecone(api_key=config.get("api_key"))

    # Define index name
    index_name = config.get("index_name")

    # Instantiate the index to interact with it
    index = pc.Index(index_name)

    index.delete(
        filter={
            "source": {"$eq": file_name}
        },
        namespace=config.get("namespace")
    )



def getvectorkm_String(question,persist_directory,embedding_model_name,emb_type = "openai",vector_type=""):
    km_path = extract_km_path(persist_directory)
    km_record = query_KMCfg(kmpath=km_path)
    config_param = km_record.config_param
    vector_type = km_record.vectortype

    if vector_type == "Pinecone":
        docs = getvectorkm_String_pinecone(question,config_param)
        return docs
    if emb_type == "openai":
        # 调用openai Embeddings
        # embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
        embeddings = OpenAIEmbeddings(openai_api_key="sk-FgmkVGYRirTVzJrjDMZ5Wi27ekHKq57xGHL2lZO6lTMuUAj3", openai_api_base="https://api.chatanywhere.tech/v1/")
        # embedding_model_name = 'shibing624/text2vec-bge-large-chinese'
    else:
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)


    # 搜索
    # question = "对经国家、省、市等有关部门认定的企业技术中心及制造业创新中心，奖补政策是怎样的？"
    # 通过目录加载向量 这里的目录就是我们持久化的目录
    # persist_directory="C:\\dev\\ai-sns\\PyTalk\\pytalk\\vector_store\\vector"
    persist_directory = os.path.abspath(persist_directory)
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    # 向量搜索 根据你的问题进行本地向量搜索
    docs = vectordb.similarity_search_with_score(question, k=4)
    print(docs)
    return docs

def getvectorkm_String_pinecone(question,config_param):

    # 将JSON字符串解析为Python字典
    params = json.loads(config_param)

    # 提取各个参数
    config = {
        "api_key": params.get("api_key"),
        "cloud": params.get("cloud"),
        "region": params.get("region"),
        "index_name": params.get("index_name"),
        "namespace": params.get("namespace"),
        "top_k": params.get("top_k"),
        "embed_model": params["embed"].get("model"),
        "embed_field_map": params["embed"].get("field_map"),
        "rerank_model": params["rerank"].get("model"),
        "rerank_top_n": params["rerank"].get("top_n"),
        "rerank_fields": params["rerank"].get("rank_fields"),
        "fields": params.get("fields")
    }


    # Initialize Pinecone client with the provided API key
    pc = Pinecone(api_key=config.get("api_key"))

    # Define index name
    index_name = config.get("index_name")

    # Instantiate the index to interact with it
    index = pc.Index(index_name)

    query = question

    reranked_results = index.search(
        namespace=config.get("namespace"),
        query={
            "top_k": config.get("top_k"),
            "inputs": {
                'text': query
            }
        },
        rerank={
            "model": config.get("rerank_model"),
            "top_n": config.get("rerank_top_n"),
            "rank_fields": config.get("rerank_fields")
        },
        fields=config.get("fields")
    )

    print(reranked_results)
    docs = transform_reranked_results(reranked_results)




    return docs



# 提取 km_path 的函数
def extract_km_path(persist_directory):
    # 首先，确认 persist_directory 是当前工作目录的子路径
    current_directory = os.getcwd()
    if not persist_directory.startswith(current_directory):
        raise ValueError("The provided persist_directory is not under the current working directory.")

    # 去掉当前工作目录的部分
    relative_path = persist_directory[len(current_directory) + 1:]  # +1 是为了去掉路径分隔符

    # 分割路径并提取 km_path
    path_parts = relative_path.split(os.path.sep)

    # 检查路径格式
    if len(path_parts) < 3 or path_parts[0] != "km":
        raise ValueError("Invalid persist_directory format. It should contain 'km' followed by km_path.")

    # 返回提取到的 km_path
    return path_parts[1]  # km_path 是第二个部分


def transform_reranked_results(reranked_results: Dict) -> List[Document]:
    # Extract hits data from reranked_results
    hits = reranked_results.get('result', {}).get('hits', [])

    # Process each hit and transform to Document format
    transformed_docs = []
    for hit in hits:
        # Extract necessary information
        _id = hit.get('_id')
        _score = hit.get('_score')
        fields = hit.get('fields', {})
        category = fields.get('category')
        source = fields.get('source')
        chunk_text = fields.get('chunk_text')

        # Construct the metadata dictionary
        metadata = {
            # '_id': _id,
            # '_score': _score,
            # 'category': category,
            'source': source
        }

        # Create a new Document object with transformed data
        document = (Document(metadata=metadata, page_content=chunk_text),_score)

        # Add the transformed document to the list
        transformed_docs.append(document)

    return transformed_docs



def get_file_content_tuple(file_path):
    # 判断文件扩展名
    _, file_extension = os.path.splitext(file_path)

    # 设定图片文件扩展名
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

    if file_extension.lower() in image_extensions:
        # 如果是图片文件，调用 image_to_base64 函数
        content = image_to_base64(file_path)
        return ("image", content, file_path)
    else:
        # 否则调用 get_file_content 函数
        content = get_file_content(file_path)
        return ("document", content, file_path)


def get_file_content(file_path):
    ext = os.path.splitext(file_path)[1].lower()  # 获取文件扩展名并转为小写

    loaders = {
        '.js': lambda path: TextLoader(path, encoding='utf8'),
        '.txt': lambda path: TextLoader(path, encoding='utf8'),
        '.sql': lambda path: TextLoader(path, encoding='utf8'),
        '.pdf': PyPDFLoader,
        '.docx': word_document.UnstructuredWordDocumentLoader,
        '.xls': excel.UnstructuredExcelLoader,
        '.xlsx': excel.UnstructuredExcelLoader,
        '.csv': csv_loader.UnstructuredCSVLoader,
        '.pptx': powerpoint.UnstructuredPowerPointLoader,
        '.md': markdown.UnstructuredMarkdownLoader,
        '.html': html.UnstructuredHTMLLoader,
        '.htm': html.UnstructuredHTMLLoader,
    }

    if ext in loaders:
        loader = loaders[ext](file_path)
        docs = loader.load()  # 数据转换
        return ''.join(doc.page_content for doc in docs)  # 连接所有的 page_content

    raise ValueError(f"Unsupported file extension: {ext}")
