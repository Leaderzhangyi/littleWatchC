#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Agent模块，用于解析用户自然语言指令并执行刷课任务
"""

import os
import re
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage

# 加载环境变量
load_dotenv()

# 导入现有刷课API
import brush_api

class AIAssistant:
    """AI助手类，用于处理用户自然语言指令"""
    
    def __init__(self):
        # 初始化LLM
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # 创建工具列表
        self.tools = [
            Tool(
                name="BrushCourse",
                func=self.brush_course,
                description="用于执行刷课任务的工具，需要提供cookies、token、course_id、chapter_range和subsection_range参数。"
            )
        ]
        
        # 初始化Agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True
        )
        
        # 指令解析提示词
        self.prompt_template = ChatPromptTemplate.from_messages([
            (
                "system",
                "你是一个智能刷课助手，能够理解用户的自然语言指令，提取关键信息并执行刷课任务。\n"
                "你需要从用户的指令中提取以下信息：\n"
                "1. cookies：用户登录的cookies\n"
                "2. token：认证token\n"
                "3. course_id：课程ID\n"
                "4. chapter_range：章节范围，如'第3章'或'第2-5章'\n"
                "5. subsection_range：小节范围，如'第5小节'或'第3-8小节'\n"
                "\n"
                "如果用户的指令中缺少某些信息，你可以向用户询问。\n"
                "如果用户的指令包含所有必要信息，你需要调用BrushCourse工具执行刷课任务。"
            ),
            ("user", "{input}")
        ])
    
    def extract_info_from_query(self, query):
        """从用户查询中提取关键信息"""
        # 使用LLM提取信息
        chain = self.prompt_template | self.llm
        response = chain.invoke({"input": query})
        
        # 解析响应，提取关键信息
        # 这里需要根据实际情况调整解析逻辑
        cookies = self._extract_cookies(response.content)
        token = self._extract_token(response.content)
        course_id = self._extract_course_id(response.content)
        chapter_range = self._extract_chapter_range(response.content)
        subsection_range = self._extract_subsection_range(response.content)
        
        return {
            "cookies": cookies,
            "token": token,
            "course_id": course_id,
            "chapter_range": chapter_range,
            "subsection_range": subsection_range
        }
    
    def _extract_cookies(self, text):
        """从文本中提取cookies"""
        # 简单的正则表达式提取，实际情况可能更复杂
        match = re.search(r'cookies?\s*[:=]\s*["\']?([^\s"\']+)["\']?', text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_token(self, text):
        """从文本中提取token"""
        match = re.search(r'token\s*[:=]\s*["\']?([^\s"\']+)["\']?', text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_course_id(self, text):
        """从文本中提取课程ID"""
        match = re.search(r'课程(?:ID|id)?\s*[:=]?\s*["\']?([^\s"\']+)["\']?', text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_chapter_range(self, text):
        """从文本中提取章节范围"""
        # 匹配"第3章"或"第2-5章"
        match = re.search(r'第(\d+)(?:-(\d+))?章', text)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            return {"start": start, "end": end}
        return None
    
    def _extract_subsection_range(self, text):
        """从文本中提取小节范围"""
        # 匹配"第5小节"或"第3-8小节"
        match = re.search(r'第(\d+)(?:-(\d+))?小节', text)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            return {"start": start, "end": end}
        return None
    
    def brush_course(self, cookies, token, course_id, chapter_range, subsection_range):
        """执行刷课任务"""
        # 准备配置
        config = {
            "X_TOKEN": token,
            "COOKIE": cookies,
            "COURSE_ID": [{"id": course_id}]
        }
        
        # 模拟回调函数
        def log_callback(msg):
            print(f"日志: {msg}")
        
        callbacks = {
            "log": log_callback,
            "progress": lambda val: print(f"进度: {val}%")
        }
        
        # 创建并启动BrushWorker
        worker = brush_api.create_brush_worker(
            config=config,
            callbacks=callbacks,
            chapter_range=chapter_range,
            subsection_range=subsection_range
        )
        
        # 执行刷课任务
        worker.start()
        
        return f"已开始刷课任务，课程ID: {course_id}，章节范围: {chapter_range}，小节范围: {subsection_range}"
    
    def handle_query(self, query):
        """处理用户查询"""
        # 提取关键信息
        info = self.extract_info_from_query(query)
        
        # 检查是否缺少信息
        missing_info = []
        for key, value in info.items():
            if not value:
                missing_info.append(key)
        
        if missing_info:
            return f"请提供以下信息：{', '.join(missing_info)}"
        
        # 执行刷课任务
        result = self.brush_course(
            info["cookies"],
            info["token"],
            info["course_id"],
            info["chapter_range"],
            info["subsection_range"]
        )
        
        return result

# 测试代码
if __name__ == "__main__":
    ai_assistant = AIAssistant()
    
    # 测试查询
    test_query = "使用cookies 'test_cookies'和token 'test_token'学习课程123456的第3章第5小节"
    result = ai_assistant.handle_query(test_query)
    print(f"结果: {result}")
