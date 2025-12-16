import sys
import json
import time
import random
import os
import requests
from threading import Thread, Event

# 全局变量（将被动态更新）
CONFIG = {
    'X_TOKEN': '',
    'COOKIE': '',
    'COURSE_ID': ''
}

# 范围设置（将被动态更新）
RANGE = None
SUBRANGE = None

class BrushWorker(Thread):
    """刷课工作线程，独立于GUI的工作线程"""
    
    def __init__(self, config, callbacks=None):
        super().__init__()
        self.config = config
        self.callbacks = callbacks or {}
        self.is_running = False
        self.stop_event = Event()
        
    def run(self):
        """执行刷课任务"""
        self.is_running = True
        
        # 更新全局配置
        global CONFIG, RANGE, SUBRANGE
        CONFIG.update(self.config)
        
        # 获取用户信息
        self._emit('log', "正在获取用户信息...")
        try:
            user_name = get_user_info(CONFIG['X_TOKEN'])
            self._emit('user_info', user_name)
        except Exception as e:
            self._emit('user_info', f"获取用户信息失败: {str(e)}")
        
        # 优先使用传入的课程配置，如果没有则从配置文件读取
        if 'courses' in self.config:
            courses = self.config['courses']
            if not courses:
                self._emit('log', "❌ 没有课程信息，程序终止")
                self._emit('finished', False, 0, 0)
                return
        else:
            # 加载课程配置
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            course_config = load_config_from_json(config_file)
            
            if not course_config:
                self._emit('log', "❌ 无法加载配置文件，程序终止")
                self._emit('finished', False, 0, 0)
                return
                
            courses = course_config.get('courses', [])
            if not courses:
                self._emit('log', "❌ 配置文件中没有课程信息，程序终止")
                self._emit('finished', False, 0, 0)
                return
            
        total_courses = len(courses)
        total_success = 0
        total_failed = 0
        
        # 输出当前范围设置
        range_info = ""
        if 'RANGE' in globals() and RANGE:
            range_info += f"章节范围: {RANGE.start+1}-{RANGE.stop} "
        
        if 'SUBRANGE' in globals() and SUBRANGE:
            start = SUBRANGE.start + 1 if SUBRANGE.start is not None else 1
            end = SUBRANGE.stop if SUBRANGE.stop is not None else "末尾"
            range_info += f"小节范围: {start}-{end}"
        
        if range_info:
            self._emit('log', f"🔧 {range_info}")
        
        self._emit('log', f"📚 计划处理 {total_courses} 个课程...")
        
        for index, course in enumerate(courses, 1):
            if self.stop_event.is_set():
                self._emit('log', "⏹️ 用户中断刷课")
                break
                
            course_id = course.get('id', '')
            course_name = course.get('name', f'课程{index}')
            
            self._emit('log', f"\n{'#'*60}")
            self._emit('log', f"🔄 [任务 {index}/{total_courses}] 正在处理课程: {course_name} (ID: {course_id})")
            self._emit('log', f"{'#'*60}")
            
            # 更新当前课程ID
            CONFIG['COURSE_ID'] = course_id
            
            # 测试认证
            self._emit('log', "🔐 测试认证有效性...")
            try:
                if not test_auth():
                    self._emit('log', "❌ 认证失败，请检查Token和Cookie是否过期")
                    total_failed += 1
                    continue
            except Exception as e:
                self._emit('log', f"❌ 认证测试出错: {str(e)}")
                total_failed += 1
                continue
                
            self._emit('log', "✅ 认证通过")
            
            # 获取课程详情
            self._emit('log', "📥 正在获取课程详情...")
            try:
                subsection_list = get_course_details()
                if not subsection_list:
                    self._emit('log', "❌ 无法获取课程详情，跳过此课程")
                    total_failed += 1
                    continue
            except Exception as e:
                self._emit('log', f"❌ 获取课程详情出错: {str(e)}")
                total_failed += 1
                continue
                
            # 开始刷课
            self._emit('log', "🚀 开始自动记录学习时间...")
            total_subsections = len(subsection_list)
            success_count = 0
            
            for idx, subsection in enumerate(subsection_list, 1):
                if self.stop_event.is_set():
                    self._emit('log', "⏹️ 用户中断刷课")
                    break
                    
                self._emit('progress', int((idx / total_subsections) * 100) * (index / total_courses))
                self._emit('log', f"\n📋 正在处理第 {idx}/{total_subsections} 个小节: {subsection['subsectionName']}")
                
                if subsection['secondTime'] == 0:
                    self._emit('log', f"   ⏭️ 跳过时长为0的小节")
                    continue
                    
                try:
                    if record_study_time(subsection):
                        success_count += 1
                        self._emit('log', f"   ✅ 成功记录")
                    else:
                        self._emit('log', f"   ❌ 记录失败")
                except Exception as e:
                    self._emit('log', f"   ❌ 记录出错: {str(e)}")
                    
                # 检查是否需要停止
                if self.stop_event.is_set():
                    break
                    
                delay = random.randint(5, 10)
                self._emit('log', f"   ⏳ 等待 {delay} 秒后继续...")
                # 使用可中断的等待
                self.stop_event.wait(delay)
            
            self._emit('log', f"\n🎉 课程 {course_name} 刷课完成！")
            self._emit('log', f"📊 总小节数: {total_subsections}")
            self._emit('log', f"✅ 成功记录: {success_count}")
            self._emit('log', f"❌ 失败记录: {total_subsections - success_count}")
            
            if success_count > 0:
                total_success += 1
            else:
                total_failed += 1
                
            # 为了防止请求过快被风控，在两个课程之间加一点冷却时间
            if index < total_courses:
                wait_time = random.randint(10, 20)
                self._emit('log', f"\n☕ 休息 {wait_time} 秒后开始下一个课程...")
                # 使用可中断的等待
                if self.stop_event.wait(wait_time):
                    break
        
        self._emit('log', f"\n🏁 所有课程处理完毕！")
        self._emit('log', f"📊 总课程数: {total_courses}")
        self._emit('log', f"✅ 成功课程: {total_success}")
        self._emit('log', f"❌ 失败课程: {total_failed}")
        
        self._emit('progress', 100)
        self._emit('finished', True, total_courses, total_success)
        
    def stop(self):
        """停止刷课"""
        self.stop_event.set()
        
    def _emit(self, signal_type, *args):
        """发送回调信号"""
        if signal_type in self.callbacks:
            try:
                self.callbacks[signal_type](*args)
            except Exception as e:
                print(f"回调执行错误: {e}")

def get_headers():
    """获取请求头"""
    return {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'basic.sc.smartedu.cn',
        'Origin': 'https://basic.sc.smartedu.cn',
        'Pragma': 'no-cache',
        'Referer': 'https://basic.sc.smartedu.cn/hd/teacherTraining/learningCourse',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'X-Token': CONFIG['X_TOKEN'],
        'Cookie': CONFIG['COOKIE'],
        'Content-Type': 'application/json;charset=UTF-8'
    }

def get_user_info(x_token):
    """获取用户信息"""
    url = "https://basic.sc.smartedu.cn/hd/teacherTraining/api/user/info"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'basic.sc.smartedu.cn',
        'Origin': 'https://basic.sc.smartedu.cn',
        'Pragma': 'no-cache',
        'Referer': 'https://basic.sc.smartedu.cn/hd/teacherTraining/learningCourse',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'X-Token': x_token,
        'Cookie': CONFIG['COOKIE'],
        'Content-Type': 'application/json;charset=UTF-8'
    }
    
    payload = {
        'token': x_token
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code == 200:
            json_response = response.json()
            if json_response.get('returnCode') == '200':
                return_data = json_response.get('returnData', {})
                user_info = return_data.get('userInfo', {})
                user_name = user_info.get('name', '未知用户')
                return user_name
            else:
                return f"获取失败: {json_response.get('returnMessage', '未知错误')}"
        else:
            return f"请求失败: {response.status_code}"
    except Exception as e:
        return f"获取用户信息出错: {str(e)}"

def get_course_details():
    """获取课程详情，提取所有章节和小节信息"""
    url = "https://basic.sc.smartedu.cn/hd/teacherTraining/api/studyCourse/getCourseDetails"
    query_params = {
        "courseId": CONFIG['COURSE_ID']
    }

    try:
        response = requests.get(url, headers=get_headers(), params=query_params, timeout=100)
        
        if response.status_code == 200:
            json_response = response.json()
            
            if json_response.get('returnCode') == '200':
                return_data = json_response.get('returnData', {})
                chapters = return_data.get('chapters', [])
                
                # 提取所有小节信息
                subsection_list = []
                for chapter_idx, chapter in enumerate(chapters[RANGE], 1):
                    chapter_id = chapter.get('id', '')
                    chapter_name = chapter.get('chapterName', '')
                    subsections = chapter.get('studySubsections', [])
                    
                    for subsection_idx, subsection in enumerate(subsections[SUBRANGE], 1):
                        subsection_id = subsection.get('id', '')
                        subsection_name = subsection.get('subsectionName', '')
                        second_time = subsection.get('secondTime', 0)
                        
                        subsection_info = {
                            'courseId': CONFIG['COURSE_ID'],
                            'chapterId': chapter_id,
                            'chapterName': chapter_name,
                            'subsectionId': subsection_id,
                            'subsectionName': subsection_name,
                            'secondTime': int(second_time) if second_time else 0
                        }
                        
                        subsection_list.append(subsection_info)
                
                return subsection_list
            else:
                return None
        else:
            return None
            
    except Exception as e:
        return None

def record_study_time(subsection_info):
    """记录学习时间"""
    # 第一步：记录小节学习时间
    record_url = "https://basic.sc.smartedu.cn/hd/teacherTraining/api/studyCourseUser/recordProcess"
    
    # 模拟真实的学习时间（使用完整视频时长）
    study_time = subsection_info['secondTime'] - 0.1
    
    payload = {
        "courseId": subsection_info['courseId'],
        "chapterId": subsection_info['chapterId'],
        "subsectionId": subsection_info['subsectionId'],
        "studyTime": study_time,
        "state": "1"  # 学习状态
    }
    
    try:
        # 发送小节学习记录请求
        response = requests.post(record_url, headers=get_headers(), data=json.dumps(payload))
        
        if response.status_code == 200:
            # 解析响应
            try:
                json_response = response.json()
                if json_response.get('returnCode') == '200':
                    # 等待一下再确认章节进度
                    time.sleep(25)
                    
                    # 第二步：确认章节学习进度
                    return confirm_chapter_process(subsection_info['chapterId'], subsection_info['chapterName'])
                else:
                    return False
            except Exception:
                return False
        else:
            return False
            
    except Exception as e:
        return False

def confirm_chapter_process(chapter_id, chapter_name):
    """确认章节学习进度"""
    chapter_url = "https://basic.sc.smartedu.cn/hd/teacherTraining/api/studyCourseUser/chapterProcess"
    query_params = {
        "chapterId": chapter_id
    }
    
    try:
        # 发送章节进度确认请求
        response = requests.get(chapter_url, headers=get_headers(), params=query_params, timeout=10)
        
        if response.status_code == 200:
            json_response = response.json()
            if json_response.get('returnCode') == '200':
                return_data = json_response.get('returnData', {})
                studySubsections = return_data.get('studySubsectionUsers', [])

                # --- 优化后的验证逻辑 ---
                if not studySubsections:
                    return False
                
                # 检查返回的小节中是否有与请求的 chapterId 匹配的项（进一步验证数据有效性）
                found_match = False
                for item in studySubsections:
                    item_chapter_id = item.get('chapterId')
                    
                    if str(item_chapter_id) == str(chapter_id):
                        found_match = True
                        break

                if found_match:
                    return True
                else:
                    return False
                # -------------------------
            else:
                return False
        else:
            return False
            
    except Exception as e:
        return False

def test_auth():
    """测试认证是否有效"""
    # 测试获取课程详情接口
    test_url = "https://basic.sc.smartedu.cn/hd/teacherTraining/api/studyCourse/getCourseDetails"
    query_params = {
        "courseId": CONFIG['COURSE_ID']
    }
    
    try:
        response = requests.get(test_url, headers=get_headers(), params=query_params, timeout=10)
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if json_response.get('returnCode') == '200':
                    return True
                else:
                    return False
            except Exception as e:
                return False
        else:
            return False
            
    except Exception as e:
        return False

def load_config_from_json(file_path):
    """从JSON文件加载配置"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            return config_data
    except Exception as e:
        return None

def save_config_to_json(file_path, config_data):
    """保存配置到JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

def create_brush_worker(config, callbacks=None, chapter_range=None, subsection_range=None):
    """创建刷课工作线程"""
    # 更新全局范围设置
    global RANGE, SUBRANGE
    
    if chapter_range:
        chapter_start = chapter_range['start'] - 1
        chapter_end = chapter_range['end']
        RANGE = slice(chapter_start, chapter_end)
    
    if subsection_range:
        subsection_start = subsection_range['start'] - 1
        subsection_end = subsection_range['end']
        if subsection_end == 0:
            SUBRANGE = slice(subsection_start, None)
        else:
            SUBRANGE = slice(subsection_start, subsection_end + 1)
    
    return BrushWorker(config, callbacks)