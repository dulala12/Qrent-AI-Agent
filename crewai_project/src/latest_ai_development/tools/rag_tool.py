
from crewai_tools import RagTool 
import os

# --- 1. 租金与预算工具 ---
price_and_budget_tool = RagTool(
    # 建议使用更清晰的 snake_case 名称
    name="price_and_budget_tool", 
    description="用于查询租金、押金、水电费、预算分配和所有财务相关知识的检索工具。",
)
price_and_budget_tool.add(
    data_type="file",
    # 路径建议使用 os.path.join 或 / 来确保跨平台兼容性
    path=os.path.join("crewai_project", "knowledge", "租金与预算 298f84ca84a0802aa0c6cb8cadff4e3c.md")
)

# --- 2. 租约与法律工具 ---
lease_and_law_tool = RagTool(
    name="lease_and_law_tool",
    description="用于查询租约条款、法律责任、合同终止、纠纷解决等法律相关问题的知识。",
)
lease_and_law_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "租约与法律 298f84ca84a0809b9c07d07208adc064.md")
)

# --- 3. 信息与访问工具 ---
information_and_access_tool = RagTool(
    name="information_and_access_tool",
    description="用于查询租房信息来源、渠道、看房预约、前期准备等相关流程的知识。",
)
information_and_access_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "租房前期：信息与渠道 298f84ca84a080689d83d2dcfb254ad6.md")
)
information_and_access_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "crewai_project\knowledge\入住与居住期 299f84ca84a0803993ecf6decceaa110(1).md")
)

# --- 4. 基础知识工具（多文件加载） ---
basic_knowledge_tool = RagTool(
    name="basic_knowledge_tool",
    description="用于查询租房常识和Qrent澳洲租房全流程攻略，提供背景和总体流程信息。",
)
basic_knowledge_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "常识资料.md")
)
basic_knowledge_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "Qrent澳洲租房全流程攻略250417版(1).pdf")
)

