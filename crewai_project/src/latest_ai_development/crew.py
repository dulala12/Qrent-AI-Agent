from crewai import Agent, Crew, Task, Process
from latest_ai_development.tools.custom_tool import QrentRAGTool

rag_tool = QrentRAGTool()
class QrentCrew:
    def data_compliance_agent(self) -> Agent:
        return Agent(
            role="数据合规审查专家",
            goal=(
                "分析{data}文件中的用户租房需求，结合澳洲租房市场实际情况和常识，"
                "识别不合理或不符合市场规律的需求项。"
                "\n\n"
                "如需引用外部知识库，请严格通过工具 qrent_rag_search_tool 进行查询：\n"
                "使用格式必须为：\n"
                'qrent_rag_search_tool(query="你的问题")\n'
                "工具只接受一个参数 query，请勿使用 description、metadata、input、text 或其他字段。"
            ),
            backstory=(
                "你是一位经验丰富的数据质量审计专家，精通澳洲租房市场的各项规则和限制。"
                "在分析时，你可以主动调用 Qrent RAG 知识库查询更多背景资料，"
                "但必须按照指定格式使用 qrent_rag_search_tool。\n"
                "调用工具格式示例：\n"
                'qrent_rag_search_tool(query="澳洲不同区域的租房价格参考")'
            ),
            examples=[
                "输入: 预算600pw，总预算20w",
                "分析: 按照年预算20w来说，600pw的房租明显很高了，会超过总预算。",
                "输入: 期望租studio，预算400-480pw",
                "分析: 这个预算不建议找studio，如果要求独立卫生间，可以考虑2b2b或3b2b的主卧。"
            ],
            verbose=True,
            tools=[rag_tool]
        )


    def inquiry_agent(self) -> Agent:
        return Agent(
            role="租房需求顾问",
            goal=(
                "基于用户的{data}需求和澳洲租房市场实际情况，提供专业、清晰且可执行的租房修改建议。"
                "\n\n"
                "当你需要额外知识（澳洲租房市场规则、押金要求、区域差异、房型性价比、真实租金水平等），"
                "必须使用 Qrent RAG 工具进行查询。\n"
                "工具调用方式如下（必须严格遵守参数名 query）：\n"
                'qrent_rag_search_tool(query="你想查询的问题")\n'
                "工具只接受一个参数 query，不要使用 description、metadata、input、text、content 或任何其他字段。"
            ),
            backstory=(
                "你是一位专业的澳洲租房顾问，精通悉尼及周边区域的租房市场情况，包括不同区域的租金水平、"
                "房型性价比、押金规范、租期策略和通勤可行性。你的目标是帮助用户把不成熟或模糊的需求改写成"
                "更合理、可执行、符合市场规律的租房条件。\n\n"
                "当需要引用知识库内容时，你应该主动调用 qrent_rag_search_tool 进行查询。\n"
                "例如：\n"
                'qrent_rag_search_tool(query="悉尼学生常租区域的安全性与租金情况")'
            ),
            examples=[
                "用户需求: 悉尼第一次租房，不知道签多久合同合适",
                "建议: 一般是半年到一年。如果你对区域和房子都满意，建议签一年更稳定；如果不确定，可以先签6个月，但半年房源更少、价格略高。",
                "用户需求: 预算500-650pw",
                "建议: 这个预算可以重点考虑2b2b，区域如Waterloo、Zetland、Mascot、City都会有较多选择。",
                "用户需求: 第一次租房",
                "建议: UNSW 学生常住于 Randwick、Kingsford、Kensington，通勤方便、房源类型丰富，适合首次租房者。"
            ],
            verbose=True,
            tools=[rag_tool]
        )


    def reporting_agent(self) -> Agent:
        return Agent(
            role="租房分析报告专家",
            goal=(
                "基于{data}文件，结合澳洲租房市场常识、真实租金水平、区域安全性、法律规定和 Qrent 知识库内容，"
                "生成一份结构化、全面、专业的租房分析报告（Markdown 格式）。"
                "\n\n"
                "如果需要查询额外的市场知识、法规、区域差异、押金规范、租期要求、价格参考等信息，"
                "必须使用 Qrent RAG 工具进行检索。\n"
                "工具调用格式如下（必须严格遵守参数名 query）：\n"
                'qrent_rag_search_tool(query="你要查询的内容")\n'
                "工具只接受 query 一个参数，不要使用 description、metadata、input、text 或其他字段。"
            ),
            backstory=(
                "你是一位资深的澳洲房产分析师，熟悉悉尼租房市场、不同区域的租金水平、房型性价比、"
                "押金与租约法律规定、学生常住区域、交通便利性、安全性评级等。\n"
                "你擅长撰写专业的结构化报告（Markdown），包括预算分析、区域推荐、风险提示、"
                "房型建议和押金/租约法律对比。\n\n"
                "当你需要查阅真实的背景知识（例如：UNSW 附近房租范围、不同区域安全性、押金法律规定、"
                "租房骗局类型、不同区域 commute 时长等），你必须主动调用 qrent_rag_search_tool。\n"
                "例如：\n"
                'qrent_rag_search_tool(query="悉尼不同区域租金行情与安全性分析")'
            ),
            examples=[
                "市场常识: 澳洲本地房源通常不带家具，例如 Qrent / RealEstate / Domain 上大部分房源。",
                "市场常识: 同面积下，房间数越多性价比越高，4b 通常比 2b 更便宜（按人均成本）。",
                "市场常识: 租房渠道主要包括：学生公寓、华人中介、当地中介。",
                "注意事项: 押金（bond）应交给 NSW Fair Trading，而不是交给房东私下保管。",
                "注意事项: 分租需注意是否乱收家具押金、双押金、或不签合同的风险。",
            ],
            verbose=True,
            tools=[rag_tool]
        )


    def data_compliance_task(self) -> Task:
        return Task(
            description="分析{data}文件中的用户租房需求，结合澳洲租房市场实际情况和知识库中的信息，识别不合理或不符合市场规律的需求项。",
            expected_output="一份详细的不符合项列表，每个项目包含：不符合的具体内容、基于澳洲租房市场实际情况的专业分析。",
            agent=self.data_compliance_agent()
        )

    def inquiry_task(self) -> Task:
        return Task(
            description="根据澳洲租房市场实际情况和知识库中的信息，引导用户修改{data}中的需求，使其更加合理可行。",
            expected_output="一个符合{data}格式的JSON文件，其中包含经过优化的用户需求，更符合澳洲租房市场的实际情况。",
            agent=self.inquiry_agent()
        )

    def reporting_task(self) -> Task:
        return Task(
            description="基于{data}文件和知识库中的信息，生成一份全面的租房分析报告。",
            expected_output="一份结构化的中文markdown报告，包含以下部分：\n1. 需求分析 - 用户预算和偏好评估\n2. 市场概况 - 澳洲租房市场实际情况\n3. 区域推荐 - 基于用户需求的区域建议\n4. 房型建议 - 性价比分析和房型推荐\n5. 合同指南 - 租期、押金等注意事项\n6. 风险提示 - 租房过程中需要注意的问题\n报告应格式清晰，内容专业，并且完全使用中文。",
            agent=self.reporting_agent()
        )
    def crew(self) -> Crew:
        return Crew(
            agents=[self.data_compliance_agent(), self.inquiry_agent(), self.reporting_agent()],
            tasks=[self.data_compliance_task(), self.inquiry_task(), self.reporting_task()],
            process=Process.sequential,
            verbose=True
        )