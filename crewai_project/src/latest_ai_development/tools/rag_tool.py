
from crewai_tools import RagTool 
import os

# --- 1. �����Ԥ�㹤�� ---
price_and_budget_tool = RagTool(
    # ����ʹ�ø������� snake_case ����
    name="price_and_budget_tool", 
    description="���ڲ�ѯ���Ѻ��ˮ��ѡ�Ԥ���������в������֪ʶ�ļ������ߡ�",
)
price_and_budget_tool.add(
    data_type="file",
    # ·������ʹ�� os.path.join �� / ��ȷ����ƽ̨������
    path=os.path.join("crewai_project", "knowledge", "�����Ԥ�� 298f84ca84a0802aa0c6cb8cadff4e3c.md")
)

# --- 2. ��Լ�뷨�ɹ��� ---
lease_and_law_tool = RagTool(
    name="lease_and_law_tool",
    description="���ڲ�ѯ��Լ����������Ρ���ͬ��ֹ�����׽���ȷ�����������֪ʶ��",
)
lease_and_law_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "��Լ�뷨�� 298f84ca84a0809b9c07d07208adc064.md")
)

# --- 3. ��Ϣ����ʹ��� ---
information_and_access_tool = RagTool(
    name="information_and_access_tool",
    description="���ڲ�ѯ�ⷿ��Ϣ��Դ������������ԤԼ��ǰ��׼����������̵�֪ʶ��",
)
information_and_access_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "�ⷿǰ�ڣ���Ϣ������ 298f84ca84a080689d83d2dcfb254ad6.md")
)
information_and_access_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "crewai_project\knowledge\��ס���ס�� 299f84ca84a0803993ecf6decceaa110(1).md")
)

# --- 4. ����֪ʶ���ߣ����ļ����أ� ---
basic_knowledge_tool = RagTool(
    name="basic_knowledge_tool",
    description="���ڲ�ѯ�ⷿ��ʶ��Qrent�����ⷿȫ���̹��ԣ��ṩ����������������Ϣ��",
)
basic_knowledge_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "��ʶ����.md")
)
basic_knowledge_tool.add(
    data_type="file",
    path=os.path.join("crewai_project", "knowledge", "Qrent�����ⷿȫ���̹���250417��(1).pdf")
)

