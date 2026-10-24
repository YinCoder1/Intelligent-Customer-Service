#client客户端的意思
import logging
from pymilvus import MilvusClient

from app import config
#日志打印
logger = logging.getLogger(__name__)

#创建客户端
# MilvueClient是作为连接和操作Milvus向量库的统一入口。只需实例化一个MilvueClient对象，后续所有的集合都可以调用client完成
#创建并返回一个MilvusClient实例
def create_client() -> MilvusClient:
    #建立连接
    client = MilvusClient(config.MILVUS_URL)
    #创建数据库
    if config.DB_NAME not in client.list_databases():
        client.create_database(db_name=config.DB_NAME)
    client.use_database(db_name=config.DB_NAME)
    return client
def ensure_collection(client: MilvusClient, recreate:bool = False):
    """幂等：存在则复用；recreate=True 才删（只给 reindex 用）"""
    if client.has_collection(collection_name=config.COLLECTION_NAME):
        if recreate:
            #打印日志，重建
            logger.warning("dropping collection %s", config.COLLECTION_NAME)
            client.drop_collection(collection_name=config.COLLECTION_NAME)
        else:
            #存在，不重建recrate=false
            logger.info("collection %s already exists", config.COLLECTION_NAME)
            return
    client.create_collection(
        collection_name=config.COLLECTION_NAME,
        dimension=config.EMBED_DIM,
        metric_type="COSINE",
    )
    logger.info("collection %s created.", config.COLLECTION_NAME)