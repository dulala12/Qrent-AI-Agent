from crewai_tools import RagTool
import os
import sys
from typing import Dict, Any, Optional

# 创建一个RagTool的包装器类，处理query参数格式问题
class RagToolWrapper:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.rag_tool = RagTool(name=name, description=description)
    
    def add(self, **kwargs):
        return self.rag_tool.add(**kwargs)
    
    def __call__(self, query: Any, **kwargs):
        # 处理query参数，支持字典格式和字符串格式
        if isinstance(query, dict):
            # 从字典中提取description字段或使用整个字典作为查询
            query_str = query.get('description', str(query))
        else:
            # 直接使用字符串
            query_str = str(query)
        
        # 使用处理后的字符串调用原始RagTool
        return self.rag_tool(query=query_str, **kwargs)

# 获取当前文件的绝对路径，然后构建知识目录的绝对路径

# 正确的路径应该是crewai_project/knowledge
# 计算项目根目录的几种可能路径
current_file = os.path.abspath(__file__)
# 方法1: 从当前文件路径计算
path_method1 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
# 方法2: 再往上走一级确保到达crewai_project目录
path_method2 = os.path.dirname(path_method1)

# 尝试找到正确的知识目录
knowledge_dir = None
possible_paths = [
    os.path.join(path_method2, "knowledge"),  # 首选: crewai_project/knowledge
    os.path.join(path_method1, "knowledge"),  # 备选: crewai_project/src/knowledge
    os.path.join(os.getcwd(), "knowledge"),   # 备选: 当前工作目录的knowledge
]

for path in possible_paths:
    if os.path.exists(path) and os.path.isdir(path):
        knowledge_dir = path
        print(f"找到知识目录: {knowledge_dir}")
        break

if not knowledge_dir:
    # 如果所有路径都失败，使用默认路径
    knowledge_dir = os.path.join(path_method2, "knowledge")
    print(f"未找到知识目录，使用默认路径: {knowledge_dir}")
    # 创建目录（如果需要）
    if not os.path.exists(knowledge_dir):
        try:
            os.makedirs(knowledge_dir)
            print(f"已创建知识目录: {knowledge_dir}")
        except Exception as e:
            print(f"创建知识目录失败: {str(e)}")

print(f"RAG工具知识目录: {knowledge_dir}")

# 验证知识目录是否存在
if not os.path.exists(knowledge_dir):
    print(f"警告: 知识目录不存在: {knowledge_dir}")
    # 尝试使用备用路径
    alternative_dir = os.path.join(os.getcwd(), "knowledge")
    if os.path.exists(alternative_dir):
        knowledge_dir = alternative_dir
        print(f"使用备用知识目录: {knowledge_dir}")

# --- 1. 租金与预算工具 ---
price_and_budget_tool = RagToolWrapper(
    name="price_and_budget_tool",
    description="用于查询租金、押金、水电费、预算分配和所有财务相关知识的检索工具。"
)
try:
    price_file = os.path.join(knowledge_dir, "租金与预算 298f84ca84a0802aa0c6cb8cadff4e3c.md")
    if os.path.exists(price_file):
        price_and_budget_tool.add(
            data_type="file",
            path=price_file
        )
        print(f"成功加载租金与预算工具: {price_file}")
    else:
        print(f"警告: 租金与预算文件不存在: {price_file}")
except Exception as e:
    print(f"加载租金与预算工具时出错: {str(e)}")

# --- 2. 租约与法律工具 ---
lease_and_law_tool = RagToolWrapper(
    name="lease_and_law_tool",
    description="用于查询租约条款、法律责任、合同终止、纠纷解决等法律相关问题的知识。"
)
try:
    lease_file = os.path.join(knowledge_dir, "租约与法律 298f84ca84a0809b9c07d07208adc064.md")
    if os.path.exists(lease_file):
        lease_and_law_tool.add(
            data_type="file",
            path=lease_file
        )
        print(f"成功加载租约与法律工具: {lease_file}")
    else:
        print(f"警告: 租约与法律文件不存在: {lease_file}")
except Exception as e:
    print(f"加载租约与法律工具时出错: {str(e)}")

# --- 3. 信息与访问工具 ---
information_and_access_tool = RagToolWrapper(
    name="information_and_access_tool",
    description="用于查询租房信息来源、渠道、看房预约、前期准备等相关流程的知识。"
)
try:
    info_file1 = os.path.join(knowledge_dir, "租房前期：信息与渠道 298f84ca84a080689d83d2dcfb254ad6.md")
    if os.path.exists(info_file1):
        information_and_access_tool.add(
            data_type="file",
            path=info_file1
        )
        print(f"成功加载租房前期信息文件: {info_file1}")
    else:
        print(f"警告: 租房前期信息文件不存在: {info_file1}")
    
    info_file2 = os.path.join(knowledge_dir, "入住与居住期 299f84ca84a0803993ecf6decceaa110(1).md")
    if os.path.exists(info_file2):
        information_and_access_tool.add(
            data_type="file",
            path=info_file2
        )
        print(f"成功加载入住与居住期文件: {info_file2}")
    else:
        print(f"警告: 入住与居住期文件不存在: {info_file2}")
except Exception as e:
    print(f"加载信息与访问工具时出错: {str(e)}")

# --- 4. 基础知识工具（多文件加载） ---
basic_knowledge_tool = RagToolWrapper(
    name="basic_knowledge_tool",
    description="用于查询租房常识和Qrent澳洲租房全流程攻略，提供背景和总体流程信息。"
)
try:
    basic_file1 = os.path.join(knowledge_dir, "常识资料.md")
    if os.path.exists(basic_file1):
        basic_knowledge_tool.add(
            data_type="file",
            path=basic_file1
        )
        print(f"成功加载常识资料文件: {basic_file1}")
    else:
        print(f"警告: 常识资料文件不存在: {basic_file1}")
    
    basic_file2 = os.path.join(knowledge_dir, "Qrent澳洲租房全流程攻略250417版(1).pdf")
    if os.path.exists(basic_file2):
        basic_knowledge_tool.add(
            data_type="file",
            path=basic_file2
        )
        print(f"成功加载Qrent澳洲租房全流程攻略文件: {basic_file2}")
    else:
        print(f"警告: Qrent澳洲租房全流程攻略文件不存在: {basic_file2}")
except Exception as e:
    print(f"加载基础知识工具时出错: {str(e)}")

print("所有RAG工具初始化完成")



