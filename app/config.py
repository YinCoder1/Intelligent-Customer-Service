#配置类文件，集中管理
import os
from dotenv import load_dotenv

load_dotenv(override=True)#加载本地环境

#Milvue
#这个写法指的是如果没有找到第一个环境变量就默认第二个值，只能携带两个参数
# MILVUS_URI = os.getenv("MILVUS_URI", "http://192.168.100.128:19530")
MILVUS_URL = os.getenv("MILVUS_URL")

#数据库名称
DB_NAME = os.getenv("DB_NAME")

#集合名，相当于表
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

#嵌入模型
EMBED_MODEL_NAME=os.getenv("EMBED_MODEL_NAME")
#嵌入维度
EMBED_DIM=int(os.getenv("EMBED_DIM"))
#嵌入批大小（一次处理的向量化条数）,控制内存占用，避免超时，限流
EMBED_BATCH_SIZE=int(os.getenv("EMBED_BATCH_SIZE"))

#检索条数
TOP_K=5
#召回倍数
RECALL_MULTIPLIER=2

#知识库
KNOWLEDGE_FILE=os.getenv("KNOWLEDGE_FILE")

#LLM模型名称
LLM_MODEL=os.getenv("LLM_MODEL")
LLM_PROVIDER=os.getenv("LLM_PROVIDER")

# 重建接口的鉴权 token（放 .env，别硬编码）存疑？不懂
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me")


# print(MILVUS_URL)
# print(DB_NAME)
# print(COLLECTION_NAME)
# print(EMBED_MODEL_NAME)
# print(EMBED_DIM)
# print(EMBED_BATCH_SIZE)
#
# print(type(MILVUS_URL))
# print(type(DB_NAME))
# print(type(COLLECTION_NAME))
# print(type(EMBED_MODEL_NAME))
# print(type(EMBED_DIM))
# print(type(EMBED_BATCH_SIZE))
