"""
智能刷课助手 - Flask 后端服务器
提供 REST API 和 WebSocket 支持
"""

import os
import json
import threading
import uuid
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging
import brush_api
from brush_api import create_brush_worker, load_config_from_json, save_config_to_json, BrushWorker


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 支持中文
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量：存储活跃的会话
active_sessions = {}


class SessionManager:
    """管理刷课会话"""
    def __init__(self):
        self.sessions = {}

    def create_session(self):
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'thread': None,
            'status': 'idle',
            'created_at': datetime.now(),
            'logs': []
        }
        return session_id

    def get_session(self, session_id):
        """获取会话"""
        return self.sessions.get(session_id)

    def update_status(self, session_id, status):
        """更新会话状态"""
        if session_id in self.sessions:
            self.sessions[session_id]['status'] = status

    def add_log(self, session_id, message, level='info'):
        """添加日志"""
        if session_id in self.sessions:
            self.sessions[session_id]['logs'].append({
                'message': message,
                'level': level,
                'time': datetime.now().isoformat()
            })

    def delete_session(self, session_id):
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]


session_manager = SessionManager()


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置文件"""
    try:
        # 支持通过 query 参数指定配置文件路径（相对当前项目目录）
        req_path = request.args.get('path', 'config.json')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 防止用户传入绝对/上级路径，resolve为基目录下的相对路径
        config_file = os.path.normpath(os.path.join(base_dir, req_path))
        if not config_file.startswith(base_dir):
            return jsonify({'success': False, 'message': '非法的配置路径'}), 400
        config_data = load_config_from_json(config_file)
        
        if config_data:
            return jsonify({
                'success': True,
                'config': config_data
            })
        else:
            return jsonify({
                'success': False,
                'message': '无法读取配置文件'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """验证 token 并返回用户信息，同时保存到配置文件"""
    try:
        data = request.json or {}
        token = data.get('X_TOKEN')
        cookie = data.get('COOKIE')

        if not token or not cookie:
            return jsonify({'success': False, 'message': '需要 X_TOKEN 和 COOKIE'}), 400

        # 保存到 brush_api.CONFIG 以便 get_user_info 使用 COOKIE
        brush_api.CONFIG['X_TOKEN'] = token
        brush_api.CONFIG['COOKIE'] = cookie

        # 也保存到磁盘配置（支持前端传入 config_path）
        req_cfg_path = data.get('config_path', 'config.json')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.normpath(os.path.join(base_dir, req_cfg_path))
        if not config_file.startswith(base_dir):
            return jsonify({'success': False, 'message': '非法的配置路径'}), 400

        cfg = load_config_from_json(config_file) or {}
        cfg['X_TOKEN'] = token
        cfg['COOKIE'] = cookie
        save_config_to_json(config_file, cfg)

        # 调用 brush_api.get_user_info 获取用户名或错误信息
        user_info = brush_api.get_user_info(token)

        return jsonify({'success': True, 'user_info': user_info})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/start-brush', methods=['POST'])
def start_brush():
    """开始刷课"""
    try:
        data = request.json
        
        # 验证输入
        if not data.get('X_TOKEN') or not data.get('COOKIE'):
            return jsonify({
                'success': False,
                'message': '请输入 X_TOKEN 和 Cookies'
            }), 400

        # 创建会话
        session_id = session_manager.create_session()
        session_manager.update_status(session_id, 'running')

        # 保存到配置文件（如果前端传入了 config_path 则使用它）
        req_cfg_path = data.get('config_path', 'config.json')
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.normpath(os.path.join(base_dir, req_cfg_path))
        if config_file.startswith(base_dir):
            cfg = load_config_from_json(config_file) or {}
            cfg['X_TOKEN'] = data['X_TOKEN']
            cfg['COOKIE'] = data['COOKIE']
            # 保存前端选中的 COURSE_ID，便于下次加载
            raw_course = data.get('course_id', '') or cfg.get('COURSE_ID', '')
            # 支持多行输入，按行拆分并去空
            course_ids = [s.strip() for s in str(raw_course).splitlines() if s.strip()]
            if course_ids:
                # 为兼容老字段，保留第一个作为 COURSE_ID
                cfg['COURSE_INPUT_ID'] = [{'id': cid} for cid in course_ids]
                # 更新 courses 字段，保存为列表的对象形式
                # cfg['courses'] = [{'id': cid} for cid in course_ids]
            else:
                # 若无输入，保持已有值
                cfg['COURSE_INPUT_ID'] = cfg.get('COURSE_INPUT_ID', '')

            save_config_to_json(config_file, cfg)

        # 准备配置
        config = {
            'X_TOKEN': data['X_TOKEN'],
            'COOKIE': data['COOKIE'],
            'COURSE_ID': data.get('COURSE_INPUT_ID', '')
        }

        # 创建并启动 BrushWorker（使用回调将日志/进度发送到 socket）
        chapter_range = data.get('chapter_range')
        subsection_range = data.get('subsection_range')

        callbacks = {
            'log': lambda msg: emit_log(session_id, msg),
            'progress': lambda val: emit_progress(session_id, val),
            'user_info': lambda info: emit_user_info(session_id, info),
            'finished': lambda success, total, count: emit_finished(session_id, success, total, count)
        }

        worker = create_brush_worker(config, callbacks=callbacks, chapter_range=chapter_range, subsection_range=subsection_range)
        session_manager.sessions[session_id]['thread'] = worker
        worker.start()

        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': '已启动刷课任务'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/stop-brush', methods=['POST'])
def stop_brush():
    """停止刷课"""
    try:
        # 停止所有活跃线程
        for session_id, session in session_manager.sessions.items():
            thr = session.get('thread')
            if thr and getattr(thr, 'is_alive', None) and thr.is_alive():
                try:
                    thr.stop()
                except Exception:
                    pass
                session_manager.update_status(session_id, 'stopped')

        return jsonify({
            'success': True,
            'message': '已停止刷课'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def emit_log(session_id, message):
    """发送日志到客户端"""
    # 解析日志消息来确定等级
    level = 'info'
    if '✅' in message:
        level = 'success'
    elif '❌' in message:
        level = 'error'
    elif '⚠️' in message or '⏹️' in message:
        level = 'warning'

    session_manager.add_log(session_id, message, level)
    socketio.emit('log', {
        'type': 'log',
        'message': message,
        'level': level,
        'session_id': session_id
    }, room=session_id)


def emit_progress(session_id, value):
    """发送进度更新"""
    socketio.emit('progress', {
        'type': 'progress',
        'value': value,
        'session_id': session_id
    }, room=session_id)


def emit_user_info(session_id, user_info):
    """发送用户信息"""
    socketio.emit('user_info', {
        'type': 'user_info',
        'user_info': user_info,
        'session_id': session_id
    }, room=session_id)


def emit_finished(session_id, success, total, success_count):
    """发送完成信息"""
    socketio.emit('finished', {
        'type': 'finished',
        'success': success,
        'total': total,
        'success_count': success_count,
        'session_id': session_id
    }, room=session_id)

    session_manager.update_status(session_id, 'finished')
    # 30 秒后清理会话
    threading.Timer(30.0, lambda: session_manager.delete_session(session_id)).start()


@socketio.on('connect')
def on_connect():
    """客户端连接"""
    logger.info(f'客户端已连接: {request.sid}')


@socketio.on('disconnect')
def on_disconnect():
    """客户端断开连接"""
    logger.info(f'客户端已断开: {request.sid}')


@socketio.on('join_session')
def on_join_session(data):
    """加入会话房间"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('joined', {'session_id': session_id})


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 智能刷课助手 - Web 服务器")
    print("=" * 60)
    print("📍 前端地址: http://localhost:5000")
    print("🔗 API 地址: http://localhost:5000/api")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
