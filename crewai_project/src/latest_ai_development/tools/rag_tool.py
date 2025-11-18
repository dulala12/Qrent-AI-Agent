import os
import dotenv
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.embeddings.dashscope import DashScopeEmbedding
from crewai.tools import tool

dotenv.load_dotenv()

API_KEY = os.getenv("BAILIAN_API_KEY")
Settings.embed_model = DashScopeEmbedding(
    model_name="text-embedding-v2",
    api_key=API_KEY
)

PERSIST_DIR = "crewai_project/Qrent_knowledge_base"

storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
index = load_index_from_storage(storage_context)

# 创建查询引擎
query_engine = index.as_query_engine(similarity_top_k=3)

def _search_qrent_knowledge(query: str) -> str:
    """
     is a internal function to search the Qrent Knowledge Base.
    """
    try:
        response = query_engine.query(query)
        return str(response)
    except Exception as e:
        return f"Error searching the Qrent Knowledge Base: {str(e)}"
        
class RAGTool:
    @tool("Qrent Knowledge Base Search")
    def search_qrent_knowledge(query: str) -> str:
        """
        Search in Qrent Knowledge Base.
        """
        try:
            response = query_engine.query(query)
            return str(response)
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
