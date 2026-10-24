#检索+粗筛
import logging

from pymilvus import MilvusClient
import json
from app import config
from rich import print as rprint


logger=logging.getLogger(__name__)
#注意这里是def不是async后续可以考虑async
def retrieve(client,embedding,query:str,top_k:int=config.TOP_K):
    #1.问题向量化embed是转向量的方法
    q_ven = embedding.embed_query(query)
    #2.多召回，给重排留空间RECALL_MULTPLIER是设置好召回的倍数，这里是2
    recall_n = top_k*config.RECALL_MULTIPLIER
    #!!!!在这里就进行了相似度计算，后面学习的时候用一下pyvector的相关内容
    results = client.search(
        collection_name=config.COLLECTION_NAME,
        data=[q_ven],
        limit=recall_n,
        output_fields=["text","chunk_id","source"],
    )[0]
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    rprint(json.dumps(results, indent=2, ensure_ascii=False))
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    #向量列表有[][]两层，所以需要[0]拿出来数据
    # 返回的结果大概是
    # [
    #     [
    #         {
    #             "id": 1,
    #             "distance": 0.87,
    #             "entity": {
    #                 "text": "命中的原文",
    #                 "chunk_id": "c001",
    #                 "source": "doc.pdf"
    #             }
    #         },
    #         ...
    #     ]
    # ]




    # 3. 粗筛：COSINE 越大越相似，取前 top_k
    #    （以后可在这里接 Cross-Encoder 重排）
    #sorted内置下降函数
    #results表示要排序的对象
    #key=...按什么排
    #reverse=true降序排列
    #[:top_k]列表切片，取前top_k个元素
    hits = sorted(results, key=lambda h: h["distance"], reverse=True)[:top_k]
    return hits
