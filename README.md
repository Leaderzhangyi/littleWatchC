# 智能刷课助手 - Web 版本

现代化的网页前端，替代 Qt GUI，更美观易用。

## 快速开始

### 1. 安装依赖

```bash
pip install flask flask-cors flask-socketio python-socketio python-engineio
```

### 2. 运行服务器

```bash
python app.py
```

### 3. 打开浏览器

访问 `http://localhost:5000`

## 功能特点

✨ **现代化界面**
- 渐变色设计，视觉效果优雅
- 响应式布局，适配各种屏幕
- 实时日志显示，进度条更新

🔐 **安全便捷**
- 自动保存 Token 和 Cookie 到配置文件
- 一键加载配置
- 支持多课程批量刷取

⚡ **高效体验**
- 实时 WebSocket 通信
- 即时日志反馈
- 后台线程执行，不阻塞界面

## 文件说明

- `index.html` - 前端页面（HTML/CSS/JavaScript）
- `app.py` - Flask 后端服务器
- `course_gui.py` - 刷课核心逻辑（复用原有代码）
- `config.json` - 配置文件（自动保存）

## 使用流程

1. **加载配置** 
   - 点击 "📂 加载配置文件" 加载已保存的配置

2. **输入认证信息**
   - 粘贴 X_TOKEN
   - 粘贴 Cookies

3. **设置范围**
   - 配置章节范围
   - 配置小节范围

4. **开始刷课**
   - 点击 "▶ 开始刷课" 开始任务
   - 实时查看日志和进度
   - 可随时点击 "⏹ 停止刷课" 中止

## 技术栈

- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **后端**: Flask + Flask-SocketIO
- **通信**: REST API + WebSocket
- **Python**: 3.8+

## 故障排除

**无法连接服务器**
- 检查 Flask 服务是否运行
- 确认端口 5000 未被占用
- 检查防火墙设置

**日志未显示**
- 检查浏览器控制台是否有 JavaScript 错误
- 确认 WebSocket 连接是否成功

**配置无法保存**
- 检查 `config.json` 文件权限
- 确保目录可写

## 对比 Qt 版本优势

| 功能 | Qt 版本 | Web 版本 |
|------|--------|---------|
| 界面美观度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 跨平台支持 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 响应速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 开发效率 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 部署难度 | 中等 | 非常简单 |

## 许可证

MIT
