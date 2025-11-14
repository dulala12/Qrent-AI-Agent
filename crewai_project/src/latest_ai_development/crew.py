from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tools import tool
from typing import List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from latest_ai_development.tools.rag_tool import (
        price_and_budget_tool,
        lease_and_law_tool,
        information_and_access_tool,
        basic_knowledge_tool
    )
    logger.info("成功导入RAG工具")
except ImportError as e:
    logger.error(f"导入RAG工具时出错: {e}")
    # 创建空工具作为备选
    class DummyTool:
        def __init__(self, name):
            self.name = name
    
    price_and_budget_tool = DummyTool("price_and_budget_tool")
    lease_and_law_tool = DummyTool("lease_and_law_tool")
    information_and_access_tool = DummyTool("information_and_access_tool")
    basic_knowledge_tool = DummyTool("basic_knowledge_tool")
    logger.warning("已创建虚拟工具作为备选")

# 确保工具在模块级别可用，以便crewai可以通过名称找到它们
__all__ = [
    'price_and_budget_tool',
    'lease_and_law_tool',
    'information_and_access_tool',
    'basic_knowledge_tool'
]
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class LatestAiDevelopment():
    """LatestAiDevelopment crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        logger.info("初始化LatestAiDevelopment类")
        # 确保配置正确加载
        try:
            # 验证配置是否存在
            if hasattr(self, 'agents_config'):
                logger.info(f"成功加载agents配置，包含 {len(self.agents_config)} 个代理配置")
            if hasattr(self, 'tasks_config'):
                logger.info(f"成功加载tasks配置，包含 {len(self.tasks_config)} 个任务配置")
        except Exception as e:
            logger.error(f"验证配置时出错: {e}")

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools


    @agent
    def data_compliance_agent(self) -> Agent:
        logger.info("创建数据合规审查专家代理")
        try:
            return Agent(
                config=self.agents_config['data_compliance_agent'], # type: ignore[index]
                tools=[price_and_budget_tool, basic_knowledge_tool],
                verbose=True
            )
        except Exception as e:
            logger.error(f"创建数据合规审查专家代理时出错: {e}")
            # 返回一个基本的代理作为备选
            return Agent(
                role="数据合规审查专家",
                goal="分析用户租房需求，识别不合理或不符合市场规律的需求项",
                backstory="你是一位经验丰富的数据质量审计专家",
                verbose=True
            )

    @agent
    def inquiry_agent(self) -> Agent:
        logger.info("创建租房需求顾问代理")
        try:
            return Agent(
                config=self.agents_config['inquiry_agent'], # type: ignore[index]
                tools=[information_and_access_tool, basic_knowledge_tool],
                verbose=True
            )
        except Exception as e:
            logger.error(f"创建租房需求顾问代理时出错: {e}")
            # 返回一个基本的代理作为备选
            return Agent(
                role="租房需求顾问",
                goal="提供专业的租房建议",
                backstory="你是一位专业的租房顾问",
                verbose=True
            )

    @agent
    def reporting_agent(self) -> Agent:
        logger.info("创建租房分析报告专家代理")
        try:
            return Agent(
                config=self.agents_config['reporting_agent'], # type: ignore[index]
                tools=[lease_and_law_tool, information_and_access_tool, basic_knowledge_tool],
                verbose=True
            )
        except Exception as e:
            logger.error(f"创建租房分析报告专家代理时出错: {e}")
            # 返回一个基本的代理作为备选
            return Agent(
                role="租房分析报告专家",
                goal="生成全面的租房分析报告",
                backstory="你是一位资深的房产分析师",
                verbose=True
            )
    


    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task


    @task
    def data_compliance_task(self) -> Task:
        logger.info("创建数据合规任务")
        try:
            return Task(
                config=self.tasks_config['data_compliance_task'],   
            )
        except Exception as e:
            logger.error(f"创建数据合规任务时出错: {e}")
            # 返回一个基本的任务作为备选
            return Task(
                description="分析用户租房需求，识别不合理或不符合市场规律的需求项",
                expected_output="一份详细的不符合项列表",
                verbose=True
            )

    @task
    def inquiry_task(self) -> Task:
        logger.info("创建需求咨询任务")
        try:
            return Task(
                config=self.tasks_config['inquiry_task'], 
            )
        except Exception as e:
            logger.error(f"创建需求咨询任务时出错: {e}")
            # 返回一个基本的任务作为备选
            return Task(
                description="根据用户需求提供专业的租房建议",
                expected_output="一份优化的用户需求建议",
                verbose=True
            )

    @task
    def reporting_task(self) -> Task:
        logger.info("创建报告生成任务")
        try:
            return Task(
                config=self.tasks_config['reporting_task'], 
                output_file='report.md'
            )
        except Exception as e:
            logger.error(f"创建报告生成任务时出错: {e}")
            # 返回一个基本的任务作为备选
            return Task(
                description="生成一份全面的租房分析报告",
                expected_output="一份结构化的中文markdown报告",
                output_file='report.md',
                verbose=True
            )

    @crew
    def crew(self) -> Crew:
        """Creates the LatestAiDevelopment crew"""
        logger.info("创建LatestAiDevelopment团队")
        try:
            # 验证代理和任务是否正确创建
            logger.info(f"团队包含 {len(self.agents)} 个代理和 {len(self.tasks)} 个任务")
            
            return Crew(
                agents=self.agents, # Automatically created by the @agent decorator
                tasks=self.tasks, # Automatically created by the @task decorator
                process=Process.sequential,
                verbose=True,
                # 添加额外的错误处理配置
                memory=True,
                planning=True
            )
        except Exception as e:
            logger.error(f"创建团队时出错: {e}")
            # 尝试创建一个最小化的团队作为备选
            from crewai import Agent, Task
            
            fallback_agent = Agent(
                role="租房顾问",
                goal="提供租房建议",
                backstory="你是一位专业的租房顾问",
                verbose=True
            )
            
            fallback_task = Task(
                description="基于用户需求生成租房建议",
                expected_output="一份简单的租房建议",
                verbose=True
            )
            
            return Crew(
                agents=[fallback_agent],
                tasks=[fallback_task],
                process=Process.sequential,
                verbose=True
            )
