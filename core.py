import requests
import json
import time
import random

# 配置常量
CONFIG = {
    'X_TOKEN': '',
    'COOKIE': ''
    # 1983474287572594688
    # 1983723370145034240
}
RANGE = slice(2,None)  
SUBRANGE = slice(7,None)
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
                
                print(f"📚 课程名称: {return_data.get('courseName', '未知')}")
                print(f"📊 章节数量: {len(chapters)}")
                
                # 提取所有小节信息
                subsection_list = []
                for chapter_idx, chapter in enumerate(chapters[RANGE], 1):
                    chapter_id = chapter.get('id', '')
                    chapter_name = chapter.get('chapterName', '')
                    subsections = chapter.get('studySubsections', [])
                    print(f"\n📖 第{chapter_idx}章: {chapter_name}")
                    
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
                        
                        print(f"   - 第{subsection_idx}节: {subsection_name}")
                        print(f"      📄 小节ID: {subsection_id}")
                        print(f"      ⏱️ 视频时长: {second_time}秒")
                
                return subsection_list
            else:
                print(f"❌ 获取失败: {json_response.get('returnMessage', '未知错误')}")
                return None
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 获取课程详情时发生错误: {e}")
        e.with_traceback()
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
    
    print("📤 发送记录请求...")
    print(f"   URL: {record_url}")
    print(f"   载荷: {payload}")
    
    try:
        # 发送小节学习记录请求
        response = requests.post(record_url, headers=get_headers(), data=json.dumps(payload))
        
        print(f"   📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ 小节记录成功: {subsection_info['chapterName']} - {subsection_info['subsectionName']}")
            print(f"   📊 记录时长: {study_time}秒 / 总时长: {subsection_info['secondTime']}秒")
            
            # 解析响应
            try:
                json_response = response.json()
                if json_response.get('returnCode') == '200':
                    print(f"   🎯 服务器确认: {json_response.get('returnMessage', '学习记录成功')}")
                    
                    # 等待一下再确认章节进度
                    print(f"   ⏳ 等待3秒后再确认章节进度...(有队列可能需要等待)")
                    time.sleep(3)
                    
                    # 第二步：确认章节学习进度
                    return confirm_chapter_process(subsection_info['chapterId'], subsection_info['chapterName'])
                else:
                    print(f"   ⚠️ 服务器返回错误: {json_response}")
                    return False
            except Exception as json_error:
                print(f"   ❌ JSON解析错误: {json_error}")
                print(f"   📄 原始响应: {response.text}")
                return False
        else:
            print(f"❌ 小节记录失败: {subsection_info['subsectionName']} (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ 记录学习时间时发生错误: {e}")
        return False

def confirm_chapter_process(chapter_id, chapter_name):
    """确认章节学习进度"""
    chapter_url = "https://basic.sc.smartedu.cn/hd/teacherTraining/api/studyCourseUser/chapterProcess"
    query_params = {
        "chapterId": chapter_id
    }
    
    print(f"   📊 查询章节进度...")
    print(f"      URL: {chapter_url}")
    print(f"      参数: {query_params}")
    
    try:
        # 发送章节进度确认请求
        response = requests.get(chapter_url, headers=get_headers(), params=query_params, timeout=10)
        
        print(f"      📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            json_response = response.json()
            if json_response.get('returnCode') == '200':
                return_data = json_response.get('returnData', {})
                studySubsections = return_data.get('studySubsectionUsers', [])

                # --- 优化后的验证逻辑 ---
                if not studySubsections:
                    print(f"   ❌ 章节进度确认失败: 服务器返回的小节列表为空。")
                    return False
                
                # 检查返回的小节中是否有与请求的 chapterId 匹配的项（进一步验证数据有效性）
                found_match = False
                for item in studySubsections:
                    # 打印每个小节的进度，并检查是否与目标 chapterId 匹配
                    item_chapter_id = item.get('chapterId')
                    item_subsection_name = item.get('subsectionName', '未知小节')
                    item_study_time = item.get('studyTime', 0)
                    
                    if str(item_chapter_id) == str(chapter_id):
                        print(f"      - ✅ 进度: {item_subsection_name} (学习时间: {item_study_time}秒)")
                        found_match = True
                    else:
                        print(f"      - ℹ️ 其他章节进度: {item_subsection_name} (学习时间: {item_study_time}秒)")


                if found_match:
                    print(f"   ✅ 章节进度确认成功: {chapter_name} 的相关小节数据已在服务器上找到。")
                    return True
                else:
                    print(f"   ❌ 章节进度确认失败: 服务器返回的小节中未找到与章节ID {chapter_id} 匹配的数据。")
                    return False
                # -------------------------
            else:
                print(f"   ❌ 章节进度确认失败: {json_response.get('returnMessage', '未知错误')}")
                return False
        else:
            print(f"   ❌ 章节进度请求失败: 状态码 {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 确认章节进度时发生错误: {e}")
        return False

def test_auth():
    """测试认证是否有效"""
    print("🔐 测试认证有效性...")
    
    # 测试获取课程详情接口
    test_url = "https://basic.sc.smartedu.cn/hd/teacherTraining/api/studyCourse/getCourseDetails"
    query_params = {
        "courseId": CONFIG['COURSE_ID']
    }
    
    try:
        response = requests.get(test_url, headers=get_headers(), params=query_params, timeout=10)
        print(f"   🔍 测试请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"   ✅ 认证有效 - 服务器返回: {json_response.get('returnCode', '未知')}")
                print(f"   📝 消息: {json_response.get('returnMessage', '无消息')}")
                return True
            except Exception as e:
                print(f"   ❌ JSON解析失败: {e}")
                print(f"   📄 原始响应: {response.text}")
                return False
        else:
            print(f"   ❌ 认证失败 - 状态码: {response.status_code}")

            return False
            
    except Exception as e:
        print(f"   ❌ 测试请求失败: {e}")
        return False

def auto_study():
    """自动刷课主函数"""
    print("🎯 开始自动刷课...")
    print("=" * 60)
    
    # 先测试认证
    if not test_auth():
        print("❌ 认证失败，请检查Token和Cookie是否过期")
        return
    
    print("\n" + "=" * 60)
    # 获取课程详情
    print("📥 正在获取课程详情...")
    subsection_list = get_course_details()
    
    if not subsection_list:
        print("❌ 无法获取课程详情，程序终止")
        return
    
    print("\n" + "=" * 60)
    print("🚀 开始自动记录学习时间...")
    
    total_subsections = len(subsection_list)
    success_count = 0
    try:
        for idx, subsection in enumerate(subsection_list, 1):
            print(f"\n📋 正在处理第 {idx}/{total_subsections} 个小节...")
            if subsection['secondTime'] == 0:
                print(f"   ⏭️ 跳过时长为0的小节: {subsection['subsectionName']}")
                continue
            if record_study_time(subsection):
                success_count += 1
            
            delay = random.randint(5, 10)
            print(f"   ⏳ 等待 {delay} 秒后继续...")
            time.sleep(delay)
        
        print("\n" + "=" * 60)
        print(f"🎉 自动刷课完成！")
        print(f"📊 总小节数: {total_subsections}")
        print(f"✅ 成功记录: {success_count}")
        print(f"❌ 失败记录: {total_subsections - success_count}")
    except:
        print("\n👋 程序退出")

if __name__ == "__main__":
    # 定义你要刷的所有课程ID列表
    COURSE_ID_LIST = [
        # '1983474287572594688',
        '1983723370145034240'
    ]

    print(f"📋 计划处理 {len(COURSE_ID_LIST)} 个课程...")

    for index, course_id in enumerate(COURSE_ID_LIST, 1):
        print("\n" + "#" * 60)
        print(f"🔄 [任务 {index}/{len(COURSE_ID_LIST)}] 正在切换到课程 ID: {course_id}")
        print("#" * 60 + "\n")

        # 核心步骤：动态修改全局配置中的 COURSE_ID
        CONFIG['COURSE_ID'] = course_id

        # 运行自动学习主程序
        try:
            auto_study()
        except Exception as e:
            print(f"❌ 课程 {course_id} 运行出错，跳过继续下一个。错误: {e}")

        #为了防止请求过快被风控，建议在两个课程之间加一点冷却时间
        if index < len(COURSE_ID_LIST):
            wait_time = random.randint(10, 20)
            print(f"\n☕ 休息 {wait_time} 秒后开始下一个课程...")
            time.sleep(wait_time)

    print("\n🏁 所有课程处理完毕！")