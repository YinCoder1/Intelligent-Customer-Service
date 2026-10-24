#使用embedding嵌入封装,开发的适合可以抽象一层出来，内部根据实际需求采用DashScope，

#这部分内容后面可以再深入研究一下，这里先暂时采用langchain
#向量化和切分的本质，将一个文档切细之后（在这里就保留部分重叠，设定每块大小和每块的切分），然后按size组装一下，再向量化
import os

from langchain_community.embeddings import DashScopeEmbeddings

from app import config

#定义一个函数，创建并返回一个实例
def create_embedding()->DashScopeEmbeddings:

    return DashScopeEmbeddings(
        model=config.EMBED_MODEL_NAME,
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"),
    )

#分批向量化
#个人问题讲解：这个函数是分批向量化，那么这个函数需要调用向量化的功能embed_documents(batch)
def embed_documents_batched(embedding,texts):
    all_vectors = []
    for i in range(0,len(texts),config.EMBED_BATCH_SIZE):
        batch = texts[i:i+config.EMBED_BATCH_SIZE]
        all_vectors.extend(embedding.embed_documents(batch))
    return all_vectors

embedding = create_embedding()
#测试用例
# print("API Key 存在:", bool(os.getenv("DASHSCOPE_API_KEY")))
# word = ["你好","这个商品质量怎么样","你觉得明天适合去旅游吗？"]
# embedding = create_embedding()
# for i in word:
#     print(i)
#     answer=embed_documents_batched(embedding,t)
#     print(answer)
#     t.append(answer)
# if t[0]==t[1]:
#     print("相同")
