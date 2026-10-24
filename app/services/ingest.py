#建库和切分
import logging

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app import config
from app.services.embedding import embed_documents_batched

logger = logging.getLogger(__name__)

def build_index(client,embedding,recreate=False):
    # 1. 幂等初始化集合
    from app.services.milvue_client import ensure_collection
    ensure_collection(client,recreate=recreate)
    #2.读文档
    docs = TextLoader(config.KNOWLEDGE_FILE,encoding="utf-8").load()

    #3.切分
    # RecursiveCharacterTextSplitter是langchain里面用于递归切分文本的类
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,#每块最大长度
        chunk_overlap=80,#相邻重叠的字符数
        separators=
        ["\n===============\n","\n", "。", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    logger.info("chunks=%d",len(chunks))

    #4.向量化
    texts=[c.page_content for c in chunks]
    vectors = embed_documents_batched(embedding,texts)

    #5.写库
    data = [
        {
            "id":i,#id
            "vector":vectors[i],#vectoes向量化结果
            "text":texts[i],#text文本内容
            "source":config.KNOWLEDGE_FILE,#source来源
            "chunk_id":i#chunk_id切分id
        }for i in range(len(texts))
    ]
    #按主键插入或更新，主键已存在就覆盖，不存在就插入
    client.upsert(collection_name=config.COLLECTION_NAME,data=data)

    #刷新到持久化存储，确保数据落盘可被检索，防止进程崩溃没写入
    client.flush(collection_name=config.COLLECTION_NAME)
    logger.info("Index built,count=%d",len(data))
    return len(data)
