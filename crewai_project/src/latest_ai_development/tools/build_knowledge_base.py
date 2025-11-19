import os
import shutil
import dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.settings import Settings
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_index.readers.dashscope.base import DashScopeParse
from llama_index.readers.dashscope.utils import ResultType

dotenv.load_dotenv()

# 使用llamaindex和dashscope构建知识库
API_KEY = os.getenv("BAILIAN_API_KEY")
Settings.embed_model = DashScopeEmbedding(
    model_name="text-embedding-v2",
    api_key=API_KEY
)

parse = DashScopeParse(result_type=ResultType.DASHSCOPE_DOCMIND, api_key=API_KEY)
documents = SimpleDirectoryReader(
    "crewai_project/knowledge",
    file_extractor={".pdf": parse, ".md": parse}
).load_data()

# 创建知识库目录
PERSIST_DIR = "crewai_project/Qrent_knowledge_base"
if os.path.exists(PERSIST_DIR):
    shutil.rmtree(PERSIST_DIR)
os.makedirs(PERSIST_DIR, exist_ok=True)

# 创建索引
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=Settings.embed_model,
    show_progress=True
)

# 保存索引
index.storage_context.persist(PERSIST_DIR)
print(f"✅ 完成！文档数: {len(index.docstore.docs)}")