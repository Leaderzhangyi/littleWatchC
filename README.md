# 智能刷课助手 - Web 版本

现代化的网页前端，替代 Qt GUI，提供更美观易用的课程自动学习解决方案。

## 项目概述

智能刷课助手是一个自动化学习辅助工具，专为在线教育平台设计，能够自动记录课程学习进度，帮助用户高效完成课程学习任务。采用现代化 Web 技术开发，提供直观的用户界面和实时的学习进度监控。

## 功能特点

### ✨ 现代化界面
- 渐变色设计，视觉效果优雅
- 响应式布局，适配各种屏幕尺寸
- 实时日志显示，进度条动态更新
- 多用户配置卡支持，便于管理多个学习账号

### 🤖 AI助手功能
- **自然语言指令**: 支持用户通过自然语言输入刷课指令
- **智能信息提取**: 自动从指令中提取cookies、token、课程ID和章节小节信息
- **AI聊天界面**: 实时对话交互，支持上下文理解
- **智能问答**: 自动询问缺失信息，提供友好提示

### 🔐 安全便捷
- 自动保存 Token 和 Cookie 到配置文件
- 一键加载配置，快速切换学习环境
- 支持多课程批量刷取，提高学习效率
- 认证有效性实时验证

### ⚡ 高效体验
- 实时 WebSocket 通信，日志即时反馈
- 后台线程执行，不阻塞用户界面
- 智能失败重试机制
- 学习进度精确到小节

### 🔧 灵活配置
- 章节范围自定义选择
- 小节范围精确控制
- 支持自定义配置文件路径
- 可中断的学习过程

## 技术架构

### 前端架构
- **技术栈**: HTML5 + CSS3 + Vanilla JavaScript
- **界面设计**: 现代化响应式布局，支持多设备访问
- **通信方式**: WebSocket 实时通信 + RESTful API
- **用户体验**: 直观的配置界面，实时进度监控

### 后端架构
- **技术栈**: Flask + Flask-SocketIO + Python-SocketIO + Python-EngineIO + LangChain + LangChain-OpenAI
- **核心组件**:
  - `app.py`: 服务器入口，API 端点管理，SocketIO 通信
  - `brush_api.py`: 刷课核心逻辑，API 调用，工作线程管理
  - `ai_agent.py`: AI助手核心模块，自然语言指令解析，智能刷课任务生成
  - `core.py`: 备用核心实现，提供命令行支持
- **数据管理**: JSON 配置文件存储用户认证信息和课程设置
- **AI组件**:
  - **LangChain**: 构建AI Agent的框架
  - **OpenAI API**: 提供大语言模型支持
  - **自然语言处理**: 解析用户指令，提取关键信息
  - **工具调用**: 调用刷课API执行任务

### 系统架构图
```
┌─────────────────┐     WebSocket     ┌─────────────────┐
│   浏览器界面    │──────────────────▶│                 │
└─────────────────┘                   │                 │
                                      │    Flask 服务   │
┌─────────────────┐     REST API      │    (app.py)     │
│   用户配置      │──────────────────▶│                 │
└─────────────────┘                   │                 │
                                      │─────────────────┤
                                      │    AI 助手模块  │
                                      │   (ai_agent.py) │
                                      │    ┌───────────┐│
                                      │    │ LangChain ││
                                      │    └───────────┘│
                                      │        │        │
                                      │    ┌───────────┐│
                                      │    │ OpenAI API││
                                      │    └───────────┘│
                                      │─────────────────┤
                                      │                 │
                                      │  刷课核心逻辑   │
                                      │  (brush_api.py) │
                                      │                 │
                                      │─────────────────┤
                                      │                 │
                                      │  外部 API 调用  │
                                      │  (requests)     │
                                      │                 │
┌─────────────────┐     JSON 文件     └─────────────────┘
│   配置存储      │◀───────────────────┘
└─────────────────┘
```

## 快速开始

### 1. 安装依赖

确保已安装 Python 3.8 或更高版本，然后执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

**requirements.txt 包含的依赖库**：
```
fastapi==0.110.0
uvicorn==0.29.0
langchain==0.1.15
langchain-openai==0.1.0
requests==2.31.0
beautifulsoup4==4.12.3
python-dotenv==1.0.1
flask==3.0.3
flask-cors==4.0.1
flask-socketio==5.3.6
python-socketio==5.11.2
python-engineio==4.8.2
uuid==1.30
```

### 2. 配置AI模型API Key

在项目根目录创建 `.env` 文件，添加您的 OpenAI API Key：

```
OPENAI_API_KEY=your_openai_api_key
```

### 3. 运行服务器

执行以下命令启动 Flask 服务器：

```bash
python app.py
```

服务器启动后，控制台将显示：
```
============================================================
🚀 智能刷课助手 - Web 服务器
============================================================
📍 前端地址: http://localhost:5000
🔗 API 地址: http://localhost:5000/api
============================================================
```

### 4. 打开浏览器

在浏览器中访问 `http://localhost:5000` 即可使用智能刷课助手的 Web 界面。

## 使用说明

### 1. 用户配置管理

- **添加配置卡**: 点击"➕ 添加用户配置"按钮创建新的用户配置
- **删除配置卡**: 点击配置卡右上角的"🗑️ 删除"按钮移除配置
- **多配置支持**: 可同时添加多个用户配置，分别管理不同的学习账号

### 2. 认证信息配置

1. **X_TOKEN**: 输入课程平台的认证令牌
2. **Cookies**: 输入浏览器中的 Cookie 信息
3. **点击登录**: 验证认证信息的有效性
4. **用户信息**: 验证成功后将显示当前登录用户的名称

### 3. 课程配置

- **课程 ID**: 输入要学习的课程 ID，支持多行输入多个课程 ID
- **配置文件路径**: 指定配置文件的保存路径（默认为 `config.json`）
- **加载配置**: 点击"📂 加载配置文件"按钮加载已保存的配置

### 4. 范围设置

- **章节范围**: 设置要学习的章节起始和结束位置
- **小节范围**: 设置要学习的小节起始和结束位置（0 表示到末尾）

### 5. 开始学习

1. 确认所有配置信息正确无误
2. 点击"▶ 开始刷课"按钮启动学习任务
3. 实时查看学习日志和进度
4. 可随时点击"⏹ 停止"按钮中断学习

### 6. 失败课程重试

- 学习完成后，若有失败的课程，"🔄 重新刷失败"按钮将变为可用
- 点击该按钮可重新学习失败的课程

### 7. AI助手使用

#### 7.1 AI助手界面
- 页面中间新增了AI助手聊天区域
- 底部文本框用于输入自然语言指令
- 右侧显示聊天历史记录

#### 7.2 自然语言指令示例

##### 7.2.1 完整指令
```
使用cookies 'your_cookies_here'和token 'your_token_here'学习课程123456的第3章第5小节
```

##### 7.2.2 部分指令（AI会询问缺失信息）
```
学习课程123456的第3章第5小节
```

##### 7.2.3 多章节小节
```
使用cookies 'your_cookies_here'和token 'your_token_here'学习课程123456的第2-5章第1-3小节
```

#### 7.3 响应示例
- 成功响应：`已开始刷课任务，课程ID: 123456，章节范围: {"start": 3, "end": 3}，小节范围: {"start": 5, "end": 5}`
- 失败响应：`请提供以下信息：cookies, token`

## API 文档

### 获取配置
```
GET /api/config?path=config.json
```

**参数**:
- `path`: 配置文件路径（可选，默认: config.json）

**响应**:
```json
{
  "success": true,
  "config": {
    "X_TOKEN": "your_token",
    "COOKIE": "your_cookie",
    "COURSE_ID": "course_id"
  }
}
```

### 登录验证
```
POST /api/login
```

**请求体**:
```json
{
  "X_TOKEN": "your_token",
  "COOKIE": "your_cookie",
  "config_path": "config.json"
}
```

**响应**:
```json
{
  "success": true,
  "user_info": "用户名"
}
```

### 开始刷课
```
POST /api/start-brush
```

**请求体**:
```json
{
  "X_TOKEN": "your_token",
  "COOKIE": "your_cookie",
  "course_id": "course_id",
  "config_path": "config.json",
  "chapter_range": { "start": 1, "end": 5 },
  "subsection_range": { "start": 1, "end": 0 }
}
```

**响应**:
```json
{
  "success": true,
  "session_id": "session_uuid",
  "message": "已启动刷课任务"
}
```

### 停止刷课
```
POST /api/stop-brush
```

**响应**:
```json
{
  "success": true,
  "message": "已停止刷课"
}
```

### 重新刷失败课程
```
POST /api/restart-failed
```

**请求体**:
```json
{
  "session_id": "original_session_id"
}
```

**响应**:
```json
{
  "success": true,
  "session_id": "new_session_uuid",
  "message": "已开始重新刷失败课程"
}
```

### AI助手API
```
POST /api/ai-assistant
```

**请求体**:
```json
{
  "query": "使用cookies 'xxx'和token 'yyy'学习课程123的第3章第5小节"
}
```

**响应**:
```json
{
  "success": true,
  "response": "已开始刷课任务，课程ID: 123，章节范围: {\"start\": 3, \"end\": 3}，小节范围: {\"start\": 5, \"end\": 5}"
}
```

## 配置文件格式

配置文件采用 JSON 格式，示例如下：

```json
{
  "X_TOKEN": "your_token_here",
  "COOKIE": "your_cookie_here",
  "COURSE_INPUT_ID": [
    { "id": "course_id_1" },
    { "id": "course_id_2" }
  ]
}
```

## 故障排除

### 无法连接服务器
- 检查 Flask 服务是否正在运行
- 确认端口 5000 未被其他程序占用
- 检查防火墙设置，确保端口开放
- 验证浏览器 URL 是否正确（应为 `http://localhost:5000`）

### 日志未显示
- 检查浏览器控制台是否有 JavaScript 错误
- 确认 WebSocket 连接是否成功建立
- 验证服务器是否正常响应 API 请求

### 配置无法保存
- 检查配置文件路径是否正确
- 确认当前用户对配置文件目录有写入权限
- 检查磁盘空间是否充足

### 认证失败
- 验证 X_TOKEN 和 Cookie 是否正确
- 确认令牌是否过期，尝试重新获取
- 检查网络连接是否正常

### 课程学习失败
- 确认课程 ID 是否正确
- 检查认证信息是否有效
- 尝试减小章节/小节范围，分批学习
- 使用"重新刷失败"功能重试

### AI助手相关问题
- **API Key无效**: 检查`.env`文件中的OpenAI API Key是否正确
- **网络问题**: 检查网络连接，确保能访问OpenAI API
- **指令解析失败**: 优化指令格式，确保包含所有必要信息
- **模型调用失败**: 查看服务器日志，检查AI模型调用是否有错误
- **API调用频率限制**: 减少调用频率，或升级OpenAI API套餐

## 命令行使用（备用）

如果 Web 界面无法使用，可直接使用命令行方式运行：

```bash
python core.py
```

**注意**: 命令行方式需要手动修改 `core.py` 文件中的配置信息。

## 与 Qt 版本对比

| 功能 | Qt 版本 | Web 版本 |
|------|--------|---------|
| 界面美观度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 跨平台支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 响应速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 开发效率 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 部署难度 | 中等 | 非常简单 |
| 多用户支持 | 有限 | 完整支持 |
| 实时监控 | 基本支持 | 完善支持 |

## 贡献指南

欢迎对项目进行贡献！请遵循以下指南：

1. **Fork 仓库**: 在 GitHub 上 Fork 本项目到您的账号
2. **创建分支**: 基于 master 分支创建功能分支
3. **提交更改**: 确保代码符合项目风格规范
4. **测试验证**: 运行测试确保功能正常
5. **提交 PR**: 提交 Pull Request 到主仓库

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/course-brush.git
cd course-brush

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python app.py
```

### 代码风格规范
- Python 代码遵循 PEP 8 规范
- JavaScript 代码使用一致的缩进和命名规范
- 提交信息使用清晰的描述

## 许可证

本项目采用 MIT 许可证。

```
MIT License

Copyright (c) 2025 智能刷课助手

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 更新日志

### v1.1.0 (2025-12-19)
- **新增AI助手功能**
  - 支持用户通过自然语言输入刷课指令
  - 添加AI聊天界面，支持实时对话
  - 集成LangChain框架，构建AI Agent
  - 支持从自然语言指令中提取关键信息
  - 自动生成刷课任务并执行
- **技术更新**
  - 添加`ai_agent.py`核心模块
  - 集成OpenAI API支持
  - 新增`.env`配置文件
  - 更新`requirements.txt`依赖库
  - 添加AI助手API端点

### v1.0.0 (2025-12-17)
- 初始版本发布
- Web 界面替代 Qt GUI
- 支持多用户配置
- 实时 WebSocket 通信
- 章节和小节范围选择
- 失败课程重试机制



**智能刷课助手** - 让在线学习更高效！ 🎓