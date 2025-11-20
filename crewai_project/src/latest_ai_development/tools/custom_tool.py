from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.embeddings.dashscope import DashScopeEmbedding
import os
import dotenv
from pathlib import Path

# ========== 1. 加载 RAG 组件 ==========
dotenv.load_dotenv()

API_KEY = os.getenv("BAILIAN_API_KEY")
Settings.embed_model = DashScopeEmbedding(
    model_name="text-embedding-v2",
    api_key=API_KEY
)

# 使用绝对路径来定位知识库，避免路径问题
# 获取当前文件的绝对路径
current_file = Path(__file__).resolve()
# 导航到crewai_project目录下的Qrent_knowledge_base
project_root = current_file.parents[3]  # ../../.. 导航到crewai_project目录
PERSIST_DIR = str(project_root / "Qrent_knowledge_base")

storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine(similarity_top_k=3)


class QrentRAGToolInput(BaseModel):
    query: str = Field(..., description="用户想要查询 qrent_knowledge_base 的文字查询")

class QrentRAGTool(BaseTool):
    name: str = "qrent_rag_search_tool"
    description: str = (
        "使用 LlamaIndex 在 qrent_knowledge_base 中进行 RAG 检索。"
        "适用于中文和英文问题，能够从 PDF/MD 知识库中召回答案。"
    )
    args_schema: Type[BaseModel] = QrentRAGToolInput

    def _run(self, query: str) -> str:
        """
        执行 RAG 检索，返回相关内容
        """
        try:
            response = query_engine.query(query)
            return str(response)
        except Exception as e:
            return f"Error searching qrent_knowledge_base: {str(e)}"