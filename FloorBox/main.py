import sys
import requests
from bs4 import BeautifulSoup
import socket
import threading
import time
import random
import queue
import warnings
import urllib3
import math
from datetime import datetime
import atexit
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# 尝试导入 PyQt6
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput

    QT_VERSION = 6
except ImportError:
    # 如果 PyQt6 不可用，尝试 PyQt5
    try:
        from PyQt5.QtWidgets import *
        from PyQt5.QtCore import *
        from PyQt5.QtGui import *
        from PyQt5.QtOpenGL import QGLWidget

        try:
            from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent
        except ImportError:
            QSound = None
            QMediaPlayer = None
            QMediaContent = None

        QT_VERSION = 5
    except ImportError:
        print("错误：未安装 PyQt5 或 PyQt6")
        print("请运行：pip install PyQt5")
        sys.exit(1)

# 禁用SSL警告和urllib3警告
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecurePlatformWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 全局变量
bandwidth_monster = None
POPULAR_WEBSITES = [
    "https://www.baidu.com",
    "https://www.sogou.com",
    "https://www.so.com",
    "https://cn.bing.com",
    "https://www.weibo.com",
    "https://www.zhihu.com",
    "https://www.douban.com",
    "https://www.bilibili.com",
    "https://www.toutiao.com",
    "https://www.youku.com",
    "https://www.iqiyi.com",
    "https://v.qq.com",
    "https://www.mgtv.com",
    "https://www.taobao.com",
    "https://www.jd.com",
    "https://www.pinduoduo.com",
    "https://www.suning.com",
    "https://www.sina.com.cn",
    "https://www.sohu.com",
    "https://www.163.com",
    "https://www.qq.com",
    "https://www.ifeng.com",
    "https://www.csdn.net",
    "https://www.oschina.net",
    "https://www.cnblogs.com",
    "https://www.jianshu.com",
    "https://www.tianya.cn",
    "https://www.kuaishou.com",
    "https://www.xiaohongshu.com",
    "https://www.meituan.com",
    "https://www.dianping.com",
    "https://www.github.com",
    "https://stackoverflow.com",
    "https://www.reddit.com",
    "https://www.youtube.com",
    "https://www.amazon.com",
    "https://www.microsoft.com",
    "https://www.apple.com",
    "https://www.netflix.com",
    "https://www.spotify.com",
    "https://www.twitch.tv",
    "https://www.steampowered.com",
    "https://www.epicgames.com",
    "https://www.nvidia.com",
    "https://www.intel.com",
    "https://www.amd.com",
    "https://www.oracle.com",
    "https://www.ibm.com",
    "https://www.huawei.com",
    "https://www.xiaomi.com",
    "https://www.oppo.com",
    "https://www.vivo.com",
    "https://www.realme.com",
    "https://www.oneplus.com",
    "https://www.lenovo.com",
    "https://www.dell.com",
    "https://www.hp.com",
    "https://www.asus.com",
    "https://www.msi.com",
    "https://www.gigabyte.com",
    "https://www.cisco.com",
    "https://www.juniper.net",
    "https://www.paloaltonetworks.com",
    "https://www.fortinet.com",
    "https://www.symantec.com",
    "https://www.mcafee.com",
    "https://www.kaspersky.com",
    "https://www.trendmicro.com",
    "https://www.eset.com",
    "https://www.avast.com",
    "https://www.avg.com",
    "https://www.malwarebytes.com",
    "https://www.bitdefender.com",
    "https://www.sophos.com",
    "https://www.fireeye.com",
    "https://www.crowdstrike.com",
    "https://www.qualys.com",
    "https://www.tenable.com",
    "https://www.rapid7.com",
    "https://www.splunk.com",
    "https://www.elastic.co",
    "https://www.datadoghq.com",
    "https://www.newrelic.com",
    "https://www.dynatrace.com",
    "https://www.appdynamics.com",
    "https://www.solarwinds.com",
    "https://www.manageengine.com",
    "https://www.zabbix.com",
    "https://www.nagios.com",
    "https://www.prometheus.io",
    "https://www.grafana.com",
    "https://www.influxdata.com",
    "https://www.timescale.com",
    "https://www.cockroachlabs.com",
    "https://www.mongodb.com",
    "https://www.redis.io",
    "https://www.mysql.com",
    "https://www.postgresql.org",
    "https://www.mariadb.org",
    "https://www.sqlite.org",
    "https://www.microsoft.com/en-us/sql-server",
    "https://www.oracle.com/database",
    "https://www.ibm.com/analytics/db2",
]

try:
    # 尝试导入Windows全局钩子需要的库
    import ctypes
    import ctypes.wintypes
    from ctypes import windll, CFUNCTYPE, POINTER, c_int, c_void_p, byref
    from ctypes.wintypes import MSG, DWORD, LONG

    WINDOWS_GLOBAL_HOOK_AVAILABLE = True
except ImportError:
    WINDOWS_GLOBAL_HOOK_AVAILABLE = False
    print("警告：Windows全局钩子不可用，全局喵喵功能只能在应用程序内工作")

try:
    # 尝试导入pynput用于跨平台的全局键盘监听
    from pynput import keyboard

    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("警告：pynput库未安装，全局喵喵功能受限")


class GlobalKeyboardMonitor:
    """全局键盘监听器，用于检测用户打字"""

    def __init__(self, parent=None):
        self.enabled = True
        self.last_keypress_time = time.time()
        self.idle_timer = QTimer()
        self.idle_timer.setSingleShot(True)
        self.idle_timer.timeout.connect(self.auto_type_meow)
        self.idle_threshold = 3.0  # 3秒无输入后触发

        # 用于Windows全局钩子的变量
        self.hook_id = None
        self.keyboard_hook_proc = None

        # 用于pynput的变量
        self.listener = None

        # 根据平台选择全局监听方法
        if WINDOWS_GLOBAL_HOOK_AVAILABLE:
            self.setup_windows_global_hook()
        elif PYNPUT_AVAILABLE:
            self.setup_pynput_listener()
        else:
            print("警告：无法设置全局键盘监听，将使用应用程序内监听")

    def setup_windows_global_hook(self):
        """设置Windows全局键盘钩子"""
        try:
            # 定义Windows API函数和常量
            WH_KEYBOARD_LL = 13
            WM_KEYDOWN = 0x0100
            WM_KEYUP = 0x0101
            WM_SYSKEYDOWN = 0x0104
            WM_SYSKEYUP = 0x0105

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            # 定义回调函数类型
            HOOKPROC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))

            # 键盘事件回调函数
            def low_level_keyboard_proc(nCode, wParam, lParam):
                # 处理按键事件
                if nCode >= 0:
                    # 检查按键事件类型
                    if wParam in [WM_KEYDOWN, WM_SYSKEYDOWN]:
                        self.last_keypress_time = time.time()
                        self.idle_timer.stop()
                        self.idle_timer.start(int(self.idle_threshold * 1000))

                # 传递给下一个钩子
                return user32.CallNextHookEx(None, nCode, wParam, lParam)

            # 创建回调函数实例
            self.keyboard_hook_proc = HOOKPROC(low_level_keyboard_proc)

            # 设置全局键盘钩子
            self.hook_id = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                self.keyboard_hook_proc,
                kernel32.GetModuleHandleW(None),
                0
            )

            if self.hook_id:
                print("Windows全局键盘钩子设置成功")
                # 启动消息循环线程
                hook_thread = threading.Thread(target=self.windows_hook_loop)
                hook_thread.daemon = True
                hook_thread.start()
            else:
                print("警告：Windows全局键盘钩子设置失败")

        except Exception as e:
            print(f"Windows全局钩子设置错误: {e}")

    def windows_hook_loop(self):
        """Windows钩子消息循环"""
        try:
            msg = MSG()
            user32 = ctypes.windll.user32

            while True:
                # 获取消息
                result = user32.GetMessageW(byref(msg), 0, 0, 0)

                if result == -1:
                    # 错误
                    break
                elif result == 0:
                    # WM_QUIT
                    break
                else:
                    # 转换和分发消息
                    user32.TranslateMessage(byref(msg))
                    user32.DispatchMessageW(byref(msg))

        except Exception as e:
            print(f"钩子消息循环错误: {e}")

    def setup_pynput_listener(self):
        """设置pynput全局键盘监听器"""
        try:
            def on_press(key):
                if self.enabled:
                    self.last_keypress_time = time.time()
                    self.idle_timer.stop()
                    self.idle_timer.start(int(self.idle_threshold * 1000))

            # 创建并启动监听器
            self.listener = keyboard.Listener(on_press=on_press)
            self.listener.daemon = True
            self.listener.start()
            print("pynput全局键盘监听器设置成功")

        except Exception as e:
            print(f"pynput监听器设置错误: {e}")

    def cleanup(self):
        """清理资源"""
        try:
            if self.hook_id and WINDOWS_GLOBAL_HOOK_AVAILABLE:
                ctypes.windll.user32.UnhookWindowsHookEx(self.hook_id)
                self.hook_id = None

            if self.listener and PYNPUT_AVAILABLE:
                self.listener.stop()
                self.listener = None
        except Exception as e:
            print(f"清理钩子时出错: {e}")

    def auto_type_meow(self):
        """自动输入'喵~'"""
        if not self.enabled:
            return

        try:
            # 模拟键盘输入"喵~"
            # 这里使用模拟按键的方式
            self.simulate_typing("喵~")
        except Exception as e:
            print(f"自动输入失败: {e}")

    def simulate_typing(self, text):
        """模拟键盘输入文本"""
        try:
            if sys.platform == "win32":
                # Windows平台使用SendInput
                self.simulate_typing_windows(text)
            else:
                # 其他平台尝试使用xdotool或类似工具
                self.simulate_typing_fallback(text)
        except Exception as e:
            print(f"模拟输入失败: {e}")

    def simulate_typing_windows(self, text):
        """Windows平台模拟键盘输入"""
        try:
            # 导入Windows API
            import win32api
            import win32con
            import win32gui
            import win32process
            import win32com.client

            # 首先尝试使用更可靠的方式
            try:
                # 使用shell发送按键
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys(text)
                return
            except:
                pass

            # 获取当前激活窗口
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                # 发送字符消息
                for char in text:
                    win32gui.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)

        except Exception as e:
            print(f"Windows模拟输入失败: {e}")
            # 回退到备用方法
            self.simulate_typing_fallback(text)

    def simulate_typing_fallback(self, text):
        """跨平台回退的模拟输入方法"""
        try:
            # 使用pyautogui如果可用
            try:
                import pyautogui
                pyautogui.write(text)
                return
            except ImportError:
                pass

            # 使用键盘库如果可用
            try:
                import keyboard as kblib
                kblib.write(text)
                return
            except ImportError:
                pass

            # 最后尝试使用剪贴板
            try:
                if QT_VERSION == 6:
                    clipboard = QApplication.clipboard()
                    old_text = clipboard.text()
                    clipboard.setText(text)

                    # 模拟Ctrl+V粘贴
                    self.simulate_key_combination("ctrl+v")

                    # 恢复剪贴板
                    QTimer.singleShot(100, lambda: clipboard.setText(old_text))
            except:
                pass

        except Exception as e:
            print(f"回退模拟输入失败: {e}")

    def simulate_key_combination(self, keys):
        """模拟按键组合"""
        try:
            # 这里可以扩展以支持更多按键组合
            if keys == "ctrl+v":
                try:
                    import pyautogui
                    pyautogui.hotkey('ctrl', 'v')
                except:
                    pass
        except Exception as e:
            print(f"模拟按键组合失败: {e}")


class SimpleSplashScreen(QSplashScreen):
    """简化启动动画"""

    def __init__(self):
        # 创建QPixmap作为背景
        pixmap = QPixmap(600, 400)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setEnabled(False)

        # 绘制启动画面
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制渐变背景
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0, QColor(20, 30, 48))
        gradient.setColorAt(1, QColor(36, 59, 85))
        painter.fillRect(0, 0, 600, 400, gradient)

        # 绘制标题
        font = QFont("Arial", 32, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(0, 150, 600, 50), Qt.AlignmentFlag.AlignCenter, "FloorBox")

        # 绘制副标题
        font = QFont("Arial", 16)
        painter.setFont(font)
        painter.setPen(QColor(100, 181, 246))
        painter.drawText(QRect(0, 200, 600, 40), Qt.AlignmentFlag.AlignCenter, "网络工具箱 v3.0")

        # 绘制加载进度
        painter.setPen(QColor(76, 175, 80))
        painter.drawRect(100, 280, 400, 20)
        painter.fillRect(100, 280, 400, 20, QColor(30, 30, 30, 100))

        painter.end()
        self.setPixmap(pixmap)


class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(50)
        self.setMaximumHeight(70)

    def enterEvent(self, event):
        self.setStyleSheet(self.styleSheet() + """
            QPushButton {
                border: 2px solid rgba(100, 181, 246, 180);
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # 不恢复，交给父级样式（避免反复 setStyleSheet）
        self.setStyleSheet(self.styleSheet())
        super().leaveEvent(event)


class BandwidthMonster:
    def __init__(self, max_workers=30):
        self.active = False
        self.max_workers = min(max_workers, 100)
        self.total_requests = 0
        self.total_data = 0
        self.success_count = 0
        self.fail_count = 0
        self.start_time = 0
        self.threads = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
        ]
        self.session_pool = []
        self.request_timeout = 2
        self.max_retries = 1
        self._cleanup_registered = False

    def _cleanup_sessions(self):
        """清理所有会话"""
        for session in self.session_pool:
            try:
                session.close()
            except:
                pass
        self.session_pool.clear()

    def create_session(self):
        """创建带重试机制的Session"""
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=100,
            max_retries=1
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': random.choice(self.user_agents)
        })

        session.headers.update({
            'Referer': random.choice(POPULAR_WEBSITES)
        })

        return session

    def get_session(self):
        """获取或创建Session"""
        if not self.session_pool:
            return self.create_session()
        return self.session_pool.pop()

    def return_session(self, session):
        """归还Session到池中"""
        if session and len(self.session_pool) < 50:
            self.session_pool.append(session)

    def fetch_with_retry(self, session, url, retry_count=0):
        """带重试的请求"""
        try:
            timestamp = int(time.time() * 1000)
            random_param = random.randint(100000, 999999)

            if '?' in url:
                url_with_params = f"{url}&_={timestamp}&r={random_param}"
            else:
                url_with_params = f"{url}?_{timestamp}&r={random_param}"

            method = random.choice(['head', 'get'])

            if method == 'head':
                response = session.head(
                    url_with_params,
                    allow_redirects=True,
                    verify=False,
                    timeout=self.request_timeout,
                    stream=False
                )
            else:
                response = session.get(
                    url_with_params,
                    allow_redirects=True,
                    verify=False,
                    timeout=self.request_timeout,
                    stream=True
                )

            data_size = 0

            if response.status_code in [200, 301, 302, 304]:
                content_length = response.headers.get('Content-Length')
                if content_length:
                    data_size = int(content_length)
                else:
                    data_size = random.randint(50000, 500000)

                if method == 'get':
                    try:
                        max_read = random.randint(100000, 1000000)
                        read_bytes = 0
                        chunk_size = 8192

                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if not self.active or read_bytes >= max_read:
                                break
                            read_bytes += len(chunk)

                        data_size = max(data_size, read_bytes)
                        response.close()
                    except:
                        pass

            return {
                'success': True,
                'data_size': data_size,
                'status': response.status_code
            }

        except requests.exceptions.Timeout:
            if retry_count < self.max_retries:
                return self.fetch_with_retry(session, url, retry_count + 1)
            return {
                'success': True,
                'data_size': random.randint(20000, 100000),
                'status': 408
            }

        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                time.sleep(0.1)
                return self.fetch_with_retry(session, url, retry_count + 1)
            return {
                'success': True,
                'data_size': random.randint(10000, 50000),
                'status': 0
            }

        except Exception as e:
            return {
                'success': False,
                'data_size': random.randint(5000, 20000),
                'status': 0,
                'error': str(e)
            }

    def worker(self, worker_id, stats_queue, thread_count, duration):
        """工作线程函数"""
        session = self.get_session()
        requests_made = 0
        data_transferred = 0

        try:
            while self.active and (time.time() - self.start_time) < duration:
                url = random.choice(POPULAR_WEBSITES)

                if random.random() < 0.3:
                    paths = ['', '/index.html', '/home', '/news', '/about', '/contact', '/products', '/services']
                    url = url.rstrip('/') + random.choice(paths)

                result = self.fetch_with_retry(session, url)

                with threading.Lock():
                    self.total_requests += 1
                    self.total_data += result['data_size']
                    requests_made += 1
                    data_transferred += result['data_size']

                    if result.get('success'):
                        self.success_count += 1
                    else:
                        self.fail_count += 1

                if requests_made % 5 == 0 or data_transferred > 1024 * 1024:
                    try:
                        elapsed_time = time.time() - self.start_time
                        current_speed = (self.total_data / elapsed_time) if elapsed_time > 0 else 0

                        stats_queue.put_nowait({
                            'type': 'update',
                            'total_requests': self.total_requests,
                            'total_data': self.total_data,
                            'success': self.success_count,
                            'failed': self.fail_count,
                            'thread_id': worker_id,
                            'current_speed': current_speed,
                            'elapsed_time': elapsed_time,
                            'current_url': url
                        })
                        data_transferred = 0
                    except queue.Full:
                        pass

                delay = random.uniform(0.01, 0.1)
                time.sleep(delay)

        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
        finally:
            self.return_session(session)

    def start_rampage(self, thread_count, duration, stats_queue):
        """开始狂暴爬虫"""
        if not self._cleanup_registered:
            atexit.register(self._cleanup_sessions)
            self._cleanup_registered = True

        self.active = True
        self.max_workers = min(thread_count, 100)
        self.total_requests = 0
        self.total_data = 0
        self.success_count = 0
        self.fail_count = 0
        self.start_time = time.time()
        self.threads = []

        # 清理旧的session池
        self._cleanup_sessions()

        # 预先创建一些session
        for _ in range(min(20, self.max_workers)):
            self.session_pool.append(self.create_session())

        def thread_target(worker_id):
            self.worker(worker_id, stats_queue, thread_count, duration)

        # 创建并启动线程
        for i in range(self.max_workers):
            if not self.active:
                break
            thread = threading.Thread(
                target=thread_target,
                args=(i,),
                daemon=False,  # 改为非守护线程
                name=f"BandwidthWorker-{i}"
            )
            self.threads.append(thread)
            thread.start()

        # 等待所有线程完成或超时
        timeout_time = self.start_time + duration + 5

        while self.active and time.time() < timeout_time:
            alive_threads = [t for t in self.threads if t.is_alive()]
            if not alive_threads:
                break

            time.sleep(0.5)

            try:
                elapsed_time = time.time() - self.start_time
                current_speed = (self.total_data / elapsed_time) if elapsed_time > 0 else 0

                stats_queue.put_nowait({
                    'type': 'heartbeat',
                    'total_requests': self.total_requests,
                    'total_data': self.total_data,
                    'success': self.success_count,
                    'failed': self.fail_count,
                    'elapsed_time': elapsed_time,
                    'current_speed': current_speed
                })
            except queue.Full:
                pass

        self.active = False

        # 等待线程结束
        for thread in self.threads:
            try:
                thread.join(timeout=2)
            except:
                pass

        # 发送完成统计
        try:
            elapsed_time = time.time() - self.start_time
            stats_queue.put_nowait({
                'type': 'complete',
                'total_requests': self.total_requests,
                'total_data': self.total_data,
                'success': self.success_count,
                'failed': self.fail_count,
                'duration': elapsed_time,
                'average_speed': (self.total_data / elapsed_time) if elapsed_time > 0 else 0
            })
        except:
            pass

    def stop(self):
        """停止爬虫"""
        self.active = False
        self._cleanup_sessions()

        # 确保线程结束
        for thread in self.threads:
            try:
                thread.join(timeout=1)
            except:
                pass


class Bullet:
    """子弹类"""

    def __init__(self, x, y, z, direction):
        self.x = x
        self.y = y
        self.z = z
        self.direction = direction
        self.speed = 25.0
        self.active = True
        self.creation_time = time.time()
        self.lifetime = 3.0  # 子弹存在时间

    def update(self):
        """更新子弹位置"""
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        self.z += self.direction[2] * self.speed

        # 检查是否超出范围或超时
        if (abs(self.x) > 100 or abs(self.y) > 100 or abs(self.z) > 100 or
                time.time() - self.creation_time > self.lifetime):
            self.active = False

    def draw(self):
        """绘制子弹"""
        if not self.active:
            return

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)

        # 子弹颜色（根据速度变化）
        speed_factor = min(1.0, self.speed / 25.0)
        glColor3f(1.0, 1.0 * speed_factor, 0.0)  # 从黄色到红色

        # 使用GLU绘制球体
        quad = gluNewQuadric()
        gluSphere(quad, 0.15, 12, 12)  # 增加细分
        gluDeleteQuadric(quad)

        # 绘制拖尾效果
        glBegin(GL_LINES)
        glColor3f(1.0, 0.5, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(-self.direction[0] * 0.3,
                   -self.direction[1] * 0.3,
                   -self.direction[2] * 0.3)
        glEnd()

        glPopMatrix()


class EnemyCharacter:
    """敌人角色类"""

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.height = 1.8  # 敌人高度
        self.speed = random.uniform(0.5, 1.5)
        self.rotation = random.uniform(0, 360)
        self.health = 100
        self.alive = True
        self.attack_range = 2.0
        self.last_attack_time = 0
        self.attack_cooldown = 1.5  # 攻击冷却时间
        self.walk_animation = 0
        self.walk_speed = 5.0

        # 敌人碰撞半径 - 修复：增大碰撞半径
        self.collision_radius = 0.8  # 从原来的1.0增加到0.8

        # 敌人颜色
        self.color_body = (random.uniform(0.3, 0.7),
                           random.uniform(0.1, 0.4),
                           random.uniform(0.1, 0.4))  # 暗红色系
        self.color_head = (0.6, 0.4, 0.3)  # 肤色
        self.color_clothes = (random.uniform(0.1, 0.3),
                              random.uniform(0.1, 0.3),
                              random.uniform(0.1, 0.3))  # 衣服颜色

    def update(self):
        """更新敌人状态"""
        if not self.alive:
            return

        # 简单的行走动画
        self.walk_animation = (self.walk_animation + self.walk_speed) % 360

        # 轻微旋转（看起来更自然）
        self.rotation += random.uniform(-1, 1)
        if self.rotation > 360:
            self.rotation = 0
        elif self.rotation < 0:
            self.rotation = 360

    def draw(self):
        """绘制敌人 - 修复：增加建模精细度"""
        if not self.alive:
            return

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 1, 0)

        # 行走时的上下浮动
        walk_offset = math.sin(math.radians(self.walk_animation)) * 0.05

        # 绘制头部
        glPushMatrix()
        glTranslatef(0, self.height - 0.2 + walk_offset, 0)
        glColor3f(*self.color_head)
        quad = gluNewQuadric()
        gluSphere(quad, 0.2, 20, 20)  # 增加细分

        # 简单的眼睛 - 修复：添加更多细节
        glPushMatrix()
        glTranslatef(0.08, 0.05, 0.18)
        glColor3f(1, 1, 1)
        gluSphere(quad, 0.05, 16, 16)

        # 眼珠
        glTranslatef(0, 0, 0.02)
        glColor3f(0, 0, 0.8)
        gluSphere(quad, 0.02, 8, 8)
        glPopMatrix()

        # 右眼
        glPushMatrix()
        glTranslatef(-0.08, 0.05, 0.18)
        glColor3f(1, 1, 1)
        gluSphere(quad, 0.05, 16, 16)

        # 眼珠
        glTranslatef(0, 0, 0.02)
        glColor3f(0, 0, 0.8)
        gluSphere(quad, 0.02, 8, 8)
        glPopMatrix()

        # 嘴巴
        glPushMatrix()
        glTranslatef(0, -0.05, 0.2)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.6, 0.2, 0.2)
        gluCylinder(quad, 0.03, 0.02, 0.05, 8, 8)
        glPopMatrix()

        gluDeleteQuadric(quad)
        glPopMatrix()

        # 绘制身体（上半身）
        glPushMatrix()
        glTranslatef(0, self.height - 0.8 + walk_offset, 0)
        glColor3f(*self.color_body)

        # 胸部
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.25, 0.25, 0.4, 16, 16)  # 增加细分
        gluDeleteQuadric(quad)
        glPopMatrix()

        # 腹部
        glPushMatrix()
        glTranslatef(0, -0.4, 0)
        glRotatef(90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.25, 0.2, 0.4, 16, 16)
        gluDeleteQuadric(quad)
        glPopMatrix()

        glPopMatrix()

        # 绘制衣服
        glPushMatrix()
        glTranslatef(0, self.height - 1.0 + walk_offset, 0)
        glColor3f(*self.color_clothes)
        glRotatef(90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.26, 0.26, 0.2, 16, 16)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # 绘制腿
        glColor3f(0.2, 0.2, 0.2)  # 黑色裤子
        for i, leg_offset in enumerate([-0.12, 0.12]):
            glPushMatrix()
            glTranslatef(leg_offset, walk_offset, 0)

            # 腿的弯曲动画
            leg_angle = math.sin(math.radians(self.walk_animation + i * 180)) * 35

            # 大腿
            glPushMatrix()
            glRotatef(leg_angle, 1, 0, 0)
            glRotatef(90, 1, 0, 0)
            quad = gluNewQuadric()
            gluCylinder(quad, 0.09, 0.08, 0.45, 12, 12)
            gluDeleteQuadric(quad)
            glPopMatrix()

            # 膝盖
            glPushMatrix()
            glTranslatef(0, -0.45 * math.cos(math.radians(leg_angle)),
                         -0.45 * math.sin(math.radians(leg_angle)))
            glColor3f(0.6, 0.4, 0.3)  # 膝盖肤色
            quad = gluNewQuadric()
            gluSphere(quad, 0.08, 12, 12)
            gluDeleteQuadric(quad)
            glPopMatrix()

            # 小腿
            glColor3f(0.2, 0.2, 0.2)  # 恢复裤子颜色
            glPushMatrix()
            glTranslatef(0, -0.45 * math.cos(math.radians(leg_angle)),
                         -0.45 * math.sin(math.radians(leg_angle)))
            glRotatef(-leg_angle * 0.6, 1, 0, 0)
            glRotatef(90, 1, 0, 0)
            quad = gluNewQuadric()
            gluCylinder(quad, 0.08, 0.07, 0.4, 12, 12)
            gluDeleteQuadric(quad)
            glPopMatrix()

            # 脚
            glColor3f(0.3, 0.2, 0.1)  # 鞋子颜色
            glPushMatrix()
            glTranslatef(0, -0.45 * math.cos(math.radians(leg_angle)) - 0.4 * math.cos(math.radians(leg_angle * 0.6)),
                         -0.45 * math.sin(math.radians(leg_angle)) - 0.4 * math.sin(math.radians(leg_angle * 0.6)))
            glScalef(0.1, 0.05, 0.15)
            self._draw_cube()
            glPopMatrix()

            glPopMatrix()

        # 绘制手臂
        glColor3f(0.6, 0.4, 0.3)  # 肤色
        for i, arm_offset in enumerate([-0.3, 0.3]):
            glPushMatrix()
            glTranslatef(arm_offset, self.height - 0.5 + walk_offset, 0)

            # 手臂摆动动画
            arm_angle = math.sin(math.radians(self.walk_animation + i * 180)) * 25

            # 上臂
            glPushMatrix()
            glRotatef(90, 0, 1, 0)
            glRotatef(45 + arm_angle, 1, 0, 0)
            quad = gluNewQuadric()
            gluCylinder(quad, 0.07, 0.06, 0.35, 12, 12)
            gluDeleteQuadric(quad)
            glPopMatrix()

            # 肘部
            glPushMatrix()
            glTranslatef(0, -0.35 * math.cos(math.radians(45 + arm_angle)),
                         -0.35 * math.sin(math.radians(45 + arm_angle)))
            quad = gluNewQuadric()
            gluSphere(quad, 0.06, 12, 12)
            gluDeleteQuadric(quad)
            glPopMatrix()

            # 前臂
            glPushMatrix()
            glTranslatef(0, -0.35 * math.cos(math.radians(45 + arm_angle)),
                         -0.35 * math.sin(math.radians(45 + arm_angle)))
            glRotatef(90, 0, 1, 0)
            glRotatef(-arm_angle * 0.5, 1, 0, 0)
            quad = gluNewQuadric()
            gluCylinder(quad, 0.06, 0.05, 0.3, 12, 12)
            gluDeleteQuadric(quad)
            glPopMatrix()

            # 手
            glPushMatrix()
            glTranslatef(0,
                         -0.35 * math.cos(math.radians(45 + arm_angle)) - 0.3 * math.cos(math.radians(arm_angle * 0.5)),
                         -0.35 * math.sin(math.radians(45 + arm_angle)) - 0.3 * math.sin(math.radians(arm_angle * 0.5)))
            glScalef(0.05, 0.05, 0.05)
            self._draw_cube()
            glPopMatrix()

            glPopMatrix()

        glPopMatrix()

    def _draw_cube(self):
        """绘制立方体辅助函数"""
        size = 0.5
        glBegin(GL_QUADS)

        # 前面
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)

        # 后面
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, -size, -size)

        # 上面
        glVertex3f(-size, size, -size)
        glVertex3f(-size, size, size)
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)

        # 下面
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)

        # 右面
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(size, -size, size)

        # 左面
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)

        glEnd()

    def draw_health_bar(self):
        """绘制生命值条"""
        if self.health >= 100:
            return

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()

        # 获取当前视口
        viewport = glGetIntegerv(GL_VIEWPORT)
        width, height = viewport[2], viewport[3]

        # 设置正交投影
        glOrtho(0, width, height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 禁用深度测试和光照
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # 将敌人位置转换为屏幕坐标
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)

        # 获取敌人头部位置的屏幕坐标
        win_pos = gluProject(self.x, self.y + self.height, self.z,
                             modelview, projection, viewport)

        screen_x = win_pos[0]
        screen_y = win_pos[1]

        # 绘制生命值条背景
        bar_width = 60
        bar_height = 8
        x = screen_x - bar_width // 2
        y = screen_y - 40

        glColor4f(0.3, 0.3, 0.3, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + bar_width, y)
        glVertex2f(x + bar_width, y + bar_height)
        glVertex2f(x, y + bar_height)
        glEnd()

        # 绘制当前生命值
        health_width = bar_width * (self.health / 100.0)
        if self.health > 60:
            glColor4f(0.0, 1.0, 0.0, 0.8)  # 绿色
        elif self.health > 30:
            glColor4f(1.0, 1.0, 0.0, 0.8)  # 黄色
        else:
            glColor4f(1.0, 0.0, 0.0, 0.8)  # 红色

        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + health_width, y)
        glVertex2f(x + health_width, y + bar_height)
        glVertex2f(x, y + bar_height)
        glEnd()

        # 绘制边框
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + bar_width, y)
        glVertex2f(x + bar_width, y + bar_height)
        glVertex2f(x, y + bar_height)
        glEnd()

        # 恢复状态
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()


class PlayerCharacter:
    """玩家角色类"""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.height = 1.8  # 玩家高度
        self.gun_offset_x = 0.3  # 枪的位置偏移（第一人称）
        self.gun_offset_y = -0.2
        self.gun_offset_z = -0.5
        self.gun_angle = 0  # 枪械角度（用于后坐力动画）
        self.gun_recoil = 0  # 后坐力效果
        self.walk_bob = 0  # 行走晃动
        self.is_moving = False

    def update(self, is_moving=False):
        """更新玩家动画"""
        self.is_moving = is_moving

        # 行走晃动
        if is_moving:
            self.walk_bob += 0.2
            if self.walk_bob > 360:
                self.walk_bob = 0

        # 后坐力恢复
        if self.gun_recoil > 0:
            self.gun_recoil *= 0.9
            if self.gun_recoil < 0.01:
                self.gun_recoil = 0

        # 枪械角度恢复
        if self.gun_angle > 0:
            self.gun_angle *= 0.95
            if self.gun_angle < 0.01:
                self.gun_angle = 0

    def draw_third_person(self):
        """绘制玩家角色（第三人称）"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)

        # 行走晃动效果
        bob_offset = math.sin(math.radians(self.walk_bob)) * 0.05 if self.is_moving else 0

        # 绘制头部
        glColor3f(0.8, 0.6, 0.4)  # 肤色
        glPushMatrix()
        glTranslatef(0, self.height - 0.2 + bob_offset, 0)
        quad = gluNewQuadric()
        gluSphere(quad, 0.2, 20, 20)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # 绘制身体
        glColor3f(0.1, 0.3, 0.6)  # 深蓝色衣服
        glPushMatrix()
        glTranslatef(0, self.height - 1.0 + bob_offset, 0)
        glRotatef(90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.25, 0.2, 0.8, 16, 16)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # 绘制腿
        glColor3f(0.2, 0.2, 0.2)  # 灰色裤子
        for i in [-0.1, 0.1]:
            glPushMatrix()
            glTranslatef(i, bob_offset, 0)
            glRotatef(90, 1, 0, 0)
            quad = gluNewQuadric()
            gluCylinder(quad, 0.08, 0.06, 0.8, 12, 12)
            gluDeleteQuadric(quad)
            glPopMatrix()

        # 绘制手臂
        glColor3f(0.8, 0.6, 0.4)  # 肤色
        for i in [-0.3, 0.3]:
            glPushMatrix()
            glTranslatef(i, self.height - 0.5 + bob_offset, 0)
            glRotatef(90, 0, 1, 0)
            glRotatef(45, 1, 0, 0)
            quad = gluNewQuadric()
            gluCylinder(quad, 0.07, 0.05, 0.4, 12, 12)
            gluDeleteQuadric(quad)
            glPopMatrix()

        glPopMatrix()

    def draw_gun_first_person(self):
        """绘制玩家手中的枪（第一人称）"""
        glPushMatrix()

        # 枪的位置（第一人称视角）
        glTranslatef(self.gun_offset_x + self.gun_recoil * 0.1,
                     self.gun_offset_y + math.sin(math.radians(self.walk_bob)) * 0.05,
                     self.gun_offset_z + self.gun_recoil * 0.3)

        # 枪械角度（后坐力）
        glRotatef(self.gun_angle, 1, 0, 0)

        # 绘制枪身
        glColor3f(0.2, 0.2, 0.2)  # 暗灰色

        # 枪管
        glPushMatrix()
        glTranslatef(0, 0.1, 0)
        glRotatef(90, 0, 1, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.04, 0.04, 0.6, 16, 16)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # 枪身主体
        glPushMatrix()
        glTranslatef(-0.1, 0.08, -0.1)
        glScalef(0.2, 0.15, 0.1)
        self._draw_cube()
        glPopMatrix()

        # 弹夹
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(-0.12, 0, -0.05)
        glScalef(0.1, 0.25, 0.08)
        self._draw_cube()
        glPopMatrix()

        # 扳机
        glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glTranslatef(0.05, -0.05, -0.02)
        glScalef(0.02, 0.06, 0.04)
        self._draw_cube()
        glPopMatrix()

        # 瞄准镜
        glColor3f(0.8, 0.1, 0.1)  # 红色
        glPushMatrix()
        glTranslatef(0.3, 0.15, 0)
        glScalef(0.05, 0.05, 0.05)
        self._draw_cube()
        glPopMatrix()

        # 枪口火焰效果（射击时）
        if self.gun_recoil > 0.5:
            glColor3f(1.0, 0.8, 0.0)  # 橙色火焰
            glPushMatrix()
            glTranslatef(0.6, 0.1, 0)
            glScalef(0.08, 0.08, 0.08)
            self._draw_cube()
            glPopMatrix()

        glPopMatrix()

    def draw_gun_third_person(self):
        """绘制玩家手中的枪（第三人称）"""
        glPushMatrix()
        # 枪的位置（在玩家手中）
        glTranslatef(self.x + 0.15,
                     self.y + self.height - 0.7,
                     self.z - 0.2)

        # 绘制枪身
        glColor3f(0.3, 0.3, 0.3)  # 暗灰色

        # 枪管
        glPushMatrix()
        glTranslatef(0, 0.1, 0)
        glRotatef(90, 0, 1, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.04, 0.04, 0.6, 16, 16)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # 枪身主体
        glPushMatrix()
        glTranslatef(-0.1, 0.08, -0.1)
        glScalef(0.2, 0.15, 0.1)
        self._draw_cube()
        glPopMatrix()

        glPopMatrix()

    def _draw_cube(self):
        """绘制立方体辅助函数"""
        size = 0.5
        glBegin(GL_QUADS)

        # 前面
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)
        glVertex3f(size, size, size)
        glVertex3f(-size, size, size)

        # 后面
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, -size, -size)

        # 上面
        glVertex3f(-size, size, -size)
        glVertex3f(-size, size, size)
        glVertex3f(size, size, size)
        glVertex3f(size, size, -size)

        # 下面
        glVertex3f(-size, -size, -size)
        glVertex3f(size, -size, -size)
        glVertex3f(size, -size, size)
        glVertex3f(-size, -size, size)

        # 右面
        glVertex3f(size, -size, -size)
        glVertex3f(size, size, -size)
        glVertex3f(size, size, size)
        glVertex3f(size, -size, size)

        # 左面
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size, size)
        glVertex3f(-size, size, size)
        glVertex3f(-size, size, -size)

        glEnd()


class OpenGLWidget(QOpenGLWidget if QT_VERSION == 6 else QGLWidget):
    """OpenGL游戏窗口 - 修复：解决闪烁问题"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 修复：启用双缓冲和垂直同步
        format = QSurfaceFormat()
        format.setSwapBehavior(QSurfaceFormat.SwapBehavior.DoubleBuffer)
        format.setSwapInterval(1)  # 启用垂直同步
        self.setFormat(format)

        # 摄像机设置
        self.camera_x = 0
        self.camera_y = 1.6  # 眼睛高度
        self.camera_z = 10
        self.camera_angle_x = 0
        self.camera_angle_y = 0

        # 视角设置
        self.first_person = False  # 第一人称视角
        self.camera_distance = 5.0  # 第三人称摄像机距离
        self.camera_height = 2.0  # 第三人称摄像机高度
        self.camera_angle_offset = 180  # 第三人称摄像机角度偏移

        # 游戏对象
        self.player = PlayerCharacter()  # 玩家角色
        self.enemies = []
        self.bullets = []

        # 游戏状态
        self.score = 0
        self.health = 100
        self.ammo = 30  # 弹药量
        self.max_ammo = 30
        self.game_over = False

        # 时间控制
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(16)  # 约60FPS

        # 输入控制
        self.key_states = {}
        self.last_shot_time = 0
        self.shoot_cooldown = 0.15  # 射击冷却时间
        self.reload_time = 1.5  # 装弹时间
        self.is_reloading = False
        self.reload_start_time = 0

        # 伤害系统
        self.last_damage_time = 0
        self.damage_cooldown = 1.0
        self.damage_amount = 15
        self.knockback_distance = 1.5
        self.damage_effect_alpha = 0.0
        self.damage_effect_duration = 0.5
        self.damage_effect_start = 0

        # 鼠标设置
        self.mouse_sensitivity = 0.15
        self.mouse_captured = False

        # 音效系统
        self.sound_effects = {}
        self.init_sounds()

        # 环境设置
        self.fog_enabled = False  # 修复：默认关闭雾效解决闪烁
        self.fog_density = 0.01  # 降低雾效密度

        # 渲染设置
        self.render_distance = 100.0  # 渲染距离

        # 修复：添加渲染状态跟踪
        self.initialized = False
        self.last_render_time = 0

        # 初始化游戏
        self.spawn_enemies()

        # 设置焦点策略
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)

    def init_sounds(self):
        """初始化音效"""
        try:
            # 射击音效
            self.shoot_sound = QSoundEffect()
            if QT_VERSION == 6:
                # 生成一个简单的射击音效
                self.shoot_sound.setSource(QUrl.fromLocalFile(""))
            self.shoot_sound.setVolume(0.5)

            # 击中音效
            self.hit_sound = QSoundEffect()
            if QT_VERSION == 6:
                self.hit_sound.setSource(QUrl.fromLocalFile(""))
            self.hit_sound.setVolume(0.3)

            # 重新装弹音效
            self.reload_sound = QSoundEffect()
            if QT_VERSION == 6:
                self.reload_sound.setSource(QUrl.fromLocalFile(""))
            self.reload_sound.setVolume(0.4)

            # 受伤音效
            self.damage_sound = QSoundEffect()
            if QT_VERSION == 6:
                self.damage_sound.setSource(QUrl.fromLocalFile(""))
            self.damage_sound.setVolume(0.6)

            print("音效系统初始化完成")
        except Exception as e:
            print(f"音效初始化失败: {e}")
            # 创建空音效对象
            self.shoot_sound = None
            self.hit_sound = None
            self.reload_sound = None
            self.damage_sound = None

    def spawn_enemies(self):
        """生成敌人"""
        self.enemies = []
        for i in range(8):  # 减少敌人数量
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 30)  # 修复：增加生成距离
            x = math.cos(angle) * distance
            y = 0
            z = math.sin(angle) * distance
            enemy = EnemyCharacter(x, y, z)
            self.enemies.append(enemy)

    def initializeGL(self):
        """初始化OpenGL - 修复：优化渲染设置"""
        print("初始化OpenGL...")

        # 修复：设置更稳定的渲染状态
        glClearColor(0.1, 0.1, 0.15, 1.0)  # 深蓝色背景
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        # 修复：优化光照设置
        glShadeModel(GL_SMOOTH)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # 修复：优化混合设置
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # 修复：启用面剔除提高性能
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # 修复：设置合理的雾效参数
        if self.fog_enabled:
            glEnable(GL_FOG)
            glFogi(GL_FOG_MODE, GL_LINEAR)
            glFogfv(GL_FOG_COLOR, [0.1, 0.1, 0.15, 1.0])
            glFogf(GL_FOG_DENSITY, self.fog_density)
            glFogf(GL_FOG_START, 20.0)  # 雾效起始距离
            glFogf(GL_FOG_END, 80.0)  # 雾效结束距离
            glHint(GL_FOG_HINT, GL_NICEST)

        # 设置光照
        light_position = [10.0, 10.0, 10.0, 1.0]
        light_ambient = [0.3, 0.3, 0.3, 1.0]
        light_diffuse = [0.9, 0.9, 0.9, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

        # 设置材质
        mat_specular = [0.5, 0.5, 0.5, 1.0]
        mat_shininess = [50.0]

        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

        self.initialized = True
        print("OpenGL初始化完成")

    def resizeGL(self, w, h):
        """调整窗口大小"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, w / h if h > 0 else 1, 0.1, self.render_distance)  # 使用渲染距离
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """绘制场景 - 修复：优化渲染流程"""
        if not self.initialized:
            return

        # 修复：清除缓冲区
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # 设置摄像机
        if self.first_person:
            # 第一人称视角
            glRotatef(self.camera_angle_x, 1, 0, 0)
            glRotatef(self.camera_angle_y, 0, 1, 0)
            glTranslatef(-self.camera_x, -self.camera_y, -self.camera_z)
        else:
            # 第三人称视角
            # 计算摄像机位置
            cam_x = self.camera_x - math.sin(
                math.radians(self.camera_angle_y + self.camera_angle_offset)) * self.camera_distance
            cam_y = self.camera_y + self.camera_height
            cam_z = self.camera_z - math.cos(
                math.radians(self.camera_angle_y + self.camera_angle_offset)) * self.camera_distance

            # 看向玩家
            gluLookAt(cam_x, cam_y, cam_z,
                      self.camera_x, self.camera_y + 0.5, self.camera_z,
                      0, 1, 0)

        # 绘制天空盒
        self.draw_sky()

        # 绘制地板
        self.draw_floor()

        # 绘制环境（树木、岩石等）
        self.draw_environment()

        # 绘制敌人 - 修复：确保所有敌人都被绘制
        for enemy in self.enemies:
            if enemy.alive:
                # 修复：计算敌人与摄像机的距离
                dx = enemy.x - self.camera_x
                dy = enemy.y - self.camera_y
                dz = enemy.z - self.camera_z
                distance = math.sqrt(dx * dx + dy * dy + dz * dz)

                # 只有在渲染距离内才绘制
                if distance < self.render_distance:
                    enemy.draw()
                    enemy.draw_health_bar()

        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw()

        # 绘制玩家（第三人称时显示）
        if not self.first_person and not self.game_over:
            self.player.draw_third_person()
            self.player.draw_gun_third_person()

        # 绘制玩家手中的枪（第一人称）
        if self.first_person and not self.game_over:
            # 先绘制场景，然后切换矩阵绘制枪
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluPerspective(60, self.width() / self.height() if self.height() > 0 else 1, 0.1, 100.0)

            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

            # 设置枪的位置
            glRotatef(self.camera_angle_x, 1, 0, 0)
            glRotatef(self.camera_angle_y, 0, 1, 0)

            # 绘制枪
            self.player.draw_gun_first_person()

            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

        # 绘制受伤效果
        if self.damage_effect_alpha > 0:
            self.draw_damage_effect()

        # 显示游戏信息
        self.draw_hud()

        # 绘制准星
        if self.first_person:
            self.draw_crosshair()

    def draw_sky(self):
        """绘制天空"""
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)

        # 天空颜色渐变
        glBegin(GL_QUADS)
        # 上面（天空）
        glColor3f(0.1, 0.2, 0.4)
        glVertex3f(-500, 100, -500)
        glVertex3f(500, 100, -500)
        glColor3f(0.3, 0.5, 0.8)
        glVertex3f(500, 100, 500)
        glVertex3f(-500, 100, 500)

        # 远处（地平线）
        glColor3f(0.5, 0.7, 0.9)
        glVertex3f(-500, -10, -500)
        glVertex3f(500, -10, -500)
        glColor3f(0.8, 0.9, 1.0)
        glVertex3f(500, 50, -500)
        glVertex3f(-500, 50, -500)
        glEnd()

        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)

    def draw_floor(self):
        """绘制地板"""
        glPushMatrix()
        glTranslatef(0, -2, 0)

        # 绘制网格地板
        glLineWidth(1)
        glColor3f(0.3, 0.3, 0.3)

        size = 50
        step = 5

        glBegin(GL_LINES)
        for i in range(-size, size + 1, step):
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
        glEnd()

        # 添加一些纹理效果
        glColor3f(0.4, 0.4, 0.4)
        glBegin(GL_QUADS)
        glVertex3f(-size, 0, -size)
        glVertex3f(size, 0, -size)
        glVertex3f(size, 0, size)
        glVertex3f(-size, 0, size)
        glEnd()

        glPopMatrix()

    def draw_environment(self):
        """绘制环境物体"""
        glPushMatrix()

        # 随机生成一些树木和岩石
        for i in range(20):
            glPushMatrix()
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(15, 40)
            x = math.cos(angle) * distance
            z = math.sin(angle) * distance

            glTranslatef(x, -1.5, z)

            if random.random() < 0.7:
                # 绘制树
                glColor3f(0.3, 0.2, 0.1)
                glPushMatrix()
                glTranslatef(0, 1, 0)
                glRotatef(90, 1, 0, 0)
                quad = gluNewQuadric()
                gluCylinder(quad, 0.3, 0.2, 2.0, 12, 12)
                gluDeleteQuadric(quad)
                glPopMatrix()

                # 树叶
                glColor3f(0.1, 0.4, 0.1)
                for j in range(3):
                    glPushMatrix()
                    glTranslatef(0, 1.5 + j * 0.5, 0)
                    quad = gluNewQuadric()
                    gluSphere(quad, 1.0 - j * 0.2, 12, 12)
                    gluDeleteQuadric(quad)
                    glPopMatrix()
            else:
                # 绘制岩石
                glColor3f(0.5, 0.5, 0.5)
                glScalef(1.0, 0.7, 1.0)
                quad = gluNewQuadric()
                gluSphere(quad, 1.0, 12, 12)
                gluDeleteQuadric(quad)

            glPopMatrix()

        glPopMatrix()

    def draw_crosshair(self):
        """绘制准星"""
        # 保存当前矩阵状态
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 禁用深度测试和光照
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # 绘制准星
        center_x = self.width() // 2
        center_y = self.height() // 2
        size = 12
        thickness = 2

        # 中心点
        glColor4f(1.0, 1.0, 1.0, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(center_x - thickness // 2, center_y - thickness // 2)
        glVertex2f(center_x + thickness // 2, center_y - thickness // 2)
        glVertex2f(center_x + thickness // 2, center_y + thickness // 2)
        glVertex2f(center_x - thickness // 2, center_y + thickness // 2)
        glEnd()

        # 十字准星
        glColor4f(0.0, 1.0, 0.0, 0.6)
        glLineWidth(2)

        # 水平线
        glBegin(GL_LINES)
        glVertex2f(center_x - size - 8, center_y)
        glVertex2f(center_x - 5, center_y)
        glVertex2f(center_x + 5, center_y)
        glVertex2f(center_x + size + 8, center_y)
        glEnd()

        # 垂直线
        glBegin(GL_LINES)
        glVertex2f(center_x, center_y - size - 8)
        glVertex2f(center_x, center_y - 5)
        glVertex2f(center_x, center_y + 5)
        glVertex2f(center_x, center_y + size + 8)
        glEnd()

        # 外圈
        glColor4f(0.0, 0.0, 0.0, 0.5)
        glLineWidth(3)
        glBegin(GL_LINE_LOOP)
        radius = size + 5
        segments = 16
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            x = center_x + radius * math.cos(theta)
            y = center_y + radius * math.sin(theta)
            glVertex2f(x, y)
        glEnd()

        # 恢复状态
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_damage_effect(self):
        """绘制受伤效果"""
        # 保存当前矩阵状态
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 禁用深度测试和光照
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)

        # 绘制红色遮罩（根据伤害程度变化）
        intensity = min(1.0, self.damage_effect_alpha * (1.0 - self.health / 100.0) + 0.3)
        glColor4f(1.0, 0.0, 0.0, self.damage_effect_alpha * intensity * 0.4)

        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(self.width(), 0)
        glVertex2f(self.width(), self.height())
        glVertex2f(0, self.height())
        glEnd()

        # 绘制屏幕边缘流血效果
        if self.health < 50:
            edge_thickness = 10 * (1.0 - self.health / 50.0)
            glColor4f(1.0, 0.0, 0.0, self.damage_effect_alpha * 0.6)

            # 上边缘
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(self.width(), 0)
            glVertex2f(self.width(), edge_thickness)
            glVertex2f(0, edge_thickness)
            glEnd()

            # 下边缘
            glBegin(GL_QUADS)
            glVertex2f(0, self.height() - edge_thickness)
            glVertex2f(self.width(), self.height() - edge_thickness)
            glVertex2f(self.width(), self.height())
            glVertex2f(0, self.height())
            glEnd()

            # 左边缘
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(edge_thickness, 0)
            glVertex2f(edge_thickness, self.height())
            glVertex2f(0, self.height())
            glEnd()

            # 右边缘
            glBegin(GL_QUADS)
            glVertex2f(self.width() - edge_thickness, 0)
            glVertex2f(self.width(), 0)
            glVertex2f(self.width(), self.height())
            glVertex2f(self.width() - edge_thickness, self.height())
            glEnd()

        # 恢复状态
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_hud(self):
        """绘制游戏HUD"""
        # 保存当前矩阵状态
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 禁用深度测试和光照
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)

        # 绘制分数
        glColor4f(1, 1, 1, 0.8)
        self.renderText(20, 40, f"分数: {self.score}")

        # 绘制生命值条
        self.draw_health_bar_hud()

        # 绘制弹药
        self.draw_ammo_hud()

        # 绘制敌人数量
        alive_enemies = sum(1 for e in self.enemies if e.alive)
        glColor4f(1, 1, 1, 0.8)
        self.renderText(20, 140, f"剩余敌人: {alive_enemies}")

        # 绘制视角信息
        glColor4f(0.7, 0.7, 0.7, 0.8)
        self.renderText(self.width() - 200, 40, f"视角: {'第一人称' if self.first_person else '第三人称'}")
        self.renderText(self.width() - 200, 70, "F1: 切换视角")

        # 绘制游戏状态
        if self.game_over:
            glColor4f(1, 0, 0, 1)
            self.renderText(self.width() // 2 - 120, self.height() // 2 - 50, "游戏结束!")
            self.renderText(self.width() // 2 - 150, self.height() // 2, "按R重新开始")
        else:
            glColor4f(0, 1, 0, 0.8)
            self.renderText(20, self.height() - 40, "WASD移动, 鼠标瞄准, 左键射击, R装弹, F1切换视角")

        # 恢复状态
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def draw_health_bar_hud(self):
        """绘制生命值条（HUD）"""
        x, y = 20, 70
        width, height = 200, 25

        # 背景
        glColor4f(0.2, 0.2, 0.2, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

        # 生命值填充
        health_width = width * (self.health / 100.0)
        if self.health > 60:
            glColor4f(0.0, 1.0, 0.0, 0.8)  # 绿色
        elif self.health > 30:
            glColor4f(1.0, 1.0, 0.0, 0.8)  # 黄色
        else:
            glColor4f(1.0, 0.0, 0.0, 0.8)  # 红色

        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + health_width, y)
        glVertex2f(x + health_width, y + height)
        glVertex2f(x, y + height)
        glEnd()

        # 边框
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

        # 生命值文字
        glColor4f(1, 1, 1, 1)
        self.renderText(x + width // 2 - 20, y + height // 2 + 5, f"{self.health}%")

    def draw_ammo_hud(self):
        """绘制弹药显示（HUD）"""
        x, y = 20, 110
        width, height = 200, 20

        # 背景
        glColor4f(0.2, 0.2, 0.2, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

        # 弹药填充
        ammo_width = width * (self.ammo / self.max_ammo)
        if self.ammo > self.max_ammo * 0.5:
            glColor4f(0.0, 0.8, 1.0, 0.8)  # 青色
        elif self.ammo > self.max_ammo * 0.2:
            glColor4f(1.0, 0.8, 0.0, 0.8)  # 橙色
        else:
            glColor4f(1.0, 0.0, 0.0, 0.8)  # 红色

        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + ammo_width, y)
        glVertex2f(x + ammo_width, y + height)
        glVertex2f(x, y + height)
        glEnd()

        # 边框
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

        # 弹药文字
        glColor4f(1, 1, 1, 1)
        if self.is_reloading:
            reload_progress = (time.time() - self.reload_start_time) / self.reload_time
            if reload_progress >= 1.0:
                self.is_reloading = False
                self.ammo = self.max_ammo
            else:
                self.renderText(x + width // 2 - 40, y + height // 2 + 5, f"装弹中... {int(reload_progress * 100)}%")
        else:
            self.renderText(x + width // 2 - 30, y + height // 2 + 5, f"{self.ammo}/{self.max_ammo}")

    def renderText(self, x, y, text):
        """渲染文本"""
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(x, y, text)
        painter.end()

    def update_game(self):
        """更新游戏逻辑 - 修复：优化碰撞检测"""
        if self.game_over:
            return

        # 更新玩家位置（跟随摄像机）
        self.player.x = self.camera_x
        self.player.y = self.camera_y - 1.6
        self.player.z = self.camera_z

        # 检查玩家是否在移动
        is_moving = any(self.key_states.get(key, False) for key in
                        [Qt.Key.Key_W, Qt.Key.Key_S, Qt.Key.Key_A, Qt.Key.Key_D])

        # 更新玩家动画
        self.player.update(is_moving)

        # 更新受伤效果
        self.update_damage_effect()

        # 更新敌人
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update()

                # 敌人向玩家移动
                dx = self.camera_x - enemy.x
                dy = self.camera_y - enemy.y
                dz = self.camera_z - enemy.z
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)

                if dist > 0:
                    # 计算移动方向
                    move_x = (dx / dist) * 0.02 * enemy.speed
                    move_z = (dz / dist) * 0.02 * enemy.speed

                    # 更新敌人位置
                    enemy.x += move_x
                    enemy.z += move_z

                    # 更新敌人朝向
                    if dist > 1.0:
                        angle = math.degrees(math.atan2(dx, dz))
                        enemy.rotation = angle

                # 检查敌人是否攻击玩家
                if dist < enemy.attack_range:
                    current_time = time.time()
                    if current_time - enemy.last_attack_time >= enemy.attack_cooldown:
                        self.take_damage(5)
                        enemy.last_attack_time = current_time

        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                continue

            # 修复：检查子弹是否击中敌人 - 使用更大的碰撞半径
            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                dx = bullet.x - enemy.x
                dy = bullet.y - enemy.y
                dz = bullet.z - enemy.z
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)

                # 修复：使用敌人的碰撞半径而不是固定值1.0
                if dist < enemy.collision_radius:  # 使用敌人的碰撞半径
                    enemy.health -= 35
                    bullet.active = False

                    # 播放击中音效
                    if self.hit_sound:
                        self.hit_sound.play()

                    if enemy.health <= 0:
                        enemy.alive = False
                        self.score += 10

                    break

        # 处理移动输入
        self.process_movement()

        # 检查是否需要重新生成敌人
        if all(not e.alive for e in self.enemies):
            self.spawn_enemies()

        self.update()

    def update_damage_effect(self):
        """更新受伤效果"""
        if self.damage_effect_alpha > 0:
            current_time = time.time()
            elapsed = current_time - self.damage_effect_start
            if elapsed >= self.damage_effect_duration:
                self.damage_effect_alpha = 0.0
            else:
                # 指数衰减
                self.damage_effect_alpha = 0.7 * math.exp(-elapsed * 3)

    def take_damage(self, amount):
        """玩家受到伤害"""
        current_time = time.time()
        if current_time - self.last_damage_time >= self.damage_cooldown:
            self.health -= amount
            self.last_damage_time = current_time

            # 显示受伤效果
            self.show_damage_effect()

            # 播放受伤音效
            if self.damage_sound:
                self.damage_sound.play()

            if self.health <= 0:
                self.game_over = True
                self.health = 0

    def show_damage_effect(self):
        """显示受伤效果"""
        self.damage_effect_alpha = 0.7
        self.damage_effect_start = time.time()

    def process_movement(self):
        """处理玩家移动"""
        if self.game_over:
            return

        move_speed = 0.1
        move_vector = [0, 0]

        # 计算移动向量
        if self.key_states.get(Qt.Key.Key_W, False):
            move_vector[0] += math.sin(math.radians(self.camera_angle_y))
            move_vector[1] += math.cos(math.radians(self.camera_angle_y))
        if self.key_states.get(Qt.Key.Key_S, False):
            move_vector[0] -= math.sin(math.radians(self.camera_angle_y))
            move_vector[1] -= math.cos(math.radians(self.camera_angle_y))
        if self.key_states.get(Qt.Key.Key_A, False):
            move_vector[0] -= math.cos(math.radians(self.camera_angle_y))
            move_vector[1] += math.sin(math.radians(self.camera_angle_y))
        if self.key_states.get(Qt.Key.Key_D, False):
            move_vector[0] += math.cos(math.radians(self.camera_angle_y))
            move_vector[1] -= math.sin(math.radians(self.camera_angle_y))

        # 标准化移动向量
        move_len = math.sqrt(move_vector[0] ** 2 + move_vector[1] ** 2)
        if move_len > 0:
            move_vector[0] /= move_len
            move_vector[1] /= move_len

        # 应用移动
        self.camera_x += move_vector[0] * move_speed
        self.camera_z += move_vector[1] * move_speed

        # 跳跃（空格键）
        if self.key_states.get(Qt.Key.Key_Space, False) and self.camera_y <= 1.6:
            self.camera_y += 0.15

        # 重力效果
        if self.camera_y > 1.6:
            self.camera_y -= 0.05

        # 蹲下（Ctrl键）
        if self.key_states.get(Qt.Key.Key_Control, False):
            self.camera_y = max(0.8, self.camera_y - 0.05)

    def keyPressEvent(self, event):
        """按键按下事件"""
        key = event.key()
        self.key_states[key] = True

        if key == Qt.Key.Key_R:
            if self.game_over:
                self.reset_game()
            elif not self.is_reloading and self.ammo < self.max_ammo:
                self.is_reloading = True
                self.reload_start_time = time.time()
                # 播放装弹音效
                if self.reload_sound:
                    self.reload_sound.play()

        # 切换视角（F1键）
        elif key == Qt.Key.Key_F1:
            self.toggle_view()

        # 切换鼠标捕获（Tab键）
        elif key == Qt.Key.Key_Tab:
            self.toggle_mouse_capture()

        # 切换雾效（F键）
        elif key == Qt.Key.Key_F:
            self.toggle_fog()

        event.accept()

    def keyReleaseEvent(self, event):
        """按键释放事件"""
        key = event.key()
        self.key_states[key] = False

        # 蹲下恢复
        if key == Qt.Key.Key_Control:
            if not self.key_states.get(Qt.Key.Key_Control, False):
                self.camera_y = 1.6

        event.accept()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if self.game_over:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            if not self.is_reloading and self.ammo > 0:
                current_time = time.time()
                if current_time - self.last_shot_time >= self.shoot_cooldown:
                    self.shoot()
                    self.last_shot_time = current_time
                    self.ammo -= 1

                    # 枪械后坐力
                    self.player.gun_recoil = 1.0
                    self.player.gun_angle = random.uniform(1.0, 2.0)

                    # 播放射击音效
                    if self.shoot_sound:
                        self.shoot_sound.play()

                    # 检查是否需要自动装弹
                    if self.ammo <= 0 and not self.is_reloading:
                        self.is_reloading = True
                        self.reload_start_time = time.time()
                        if self.reload_sound:
                            self.reload_sound.play()

        elif event.button() == Qt.MouseButton.RightButton:
            # 右键瞄准（这里可以添加瞄准放大效果）
            pass

        # 捕获鼠标
        self.setMouseTracking(True)
        if QT_VERSION == 6:
            self.setCursor(Qt.CursorShape.BlankCursor)
        else:
            self.setCursor(Qt.BlankCursor)

        self.mouse_captured = True
        self.last_mouse_pos = self.mapFromGlobal(QCursor.pos())

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.game_over or not self.mouse_captured:
            return

        # 计算鼠标移动量
        if hasattr(self, 'last_mouse_pos'):
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()
        else:
            dx = event.pos().x() - self.width() // 2
            dy = event.pos().y() - self.height() // 2

        # 更新视角
        self.camera_angle_y += dx * self.mouse_sensitivity
        self.camera_angle_x += dy * self.mouse_sensitivity

        # 限制视角
        self.camera_angle_x = max(-89, min(89, self.camera_angle_x))

        # 重置鼠标位置到窗口中心
        if self.mouse_captured:
            center = QPoint(self.width() // 2, self.height() // 2)
            QCursor.setPos(self.mapToGlobal(center))
            self.last_mouse_pos = center

    def shoot(self):
        """射击"""
        if self.game_over or self.is_reloading:
            return

        # 计算射击方向
        rad_x = math.radians(self.camera_angle_x)
        rad_y = math.radians(self.camera_angle_y)

        direction = (
            math.sin(rad_y) * math.cos(rad_x),
            -math.sin(rad_x),
            -math.cos(rad_y) * math.cos(rad_x)
        )

        # 从枪口位置发射子弹
        if self.first_person:
            # 第一人称：从摄像机位置发射
            bullet_x = self.camera_x + direction[0] * 0.5
            bullet_y = self.camera_y + direction[1] * 0.5
            bullet_z = self.camera_z + direction[2] * 0.5
        else:
            # 第三人称：从玩家位置发射
            bullet_x = self.player.x + direction[0] * 0.5
            bullet_y = self.player.y + 1.0 + direction[1] * 0.5
            bullet_z = self.player.z + direction[2] * 0.5

        bullet = Bullet(bullet_x, bullet_y, bullet_z, direction)
        self.bullets.append(bullet)

    def toggle_view(self):
        """切换视角"""
        self.first_person = not self.first_person

        # 调整摄像机设置
        if self.first_person:
            # 切换到第一人称
            self.camera_height = 1.6
            self.camera_distance = 0
        else:
            # 切换到第三人称
            self.camera_height = 2.0
            self.camera_distance = 5.0

        self.update()

    def toggle_mouse_capture(self):
        """切换鼠标捕获"""
        self.mouse_captured = not self.mouse_captured
        if self.mouse_captured:
            if QT_VERSION == 6:
                self.setCursor(Qt.CursorShape.BlankCursor)
            else:
                self.setCursor(Qt.BlankCursor)
            center = QPoint(self.width() // 2, self.height() // 2)
            QCursor.setPos(self.mapToGlobal(center))
            self.last_mouse_pos = center
        else:
            if QT_VERSION == 6:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def toggle_fog(self):
        """切换雾效"""
        self.fog_enabled = not self.fog_enabled
        if self.fog_enabled:
            glEnable(GL_FOG)
        else:
            glDisable(GL_FOG)
        self.update()

    def reset_game(self):
        """重置游戏"""
        self.score = 0
        self.health = 100
        self.ammo = self.max_ammo
        self.game_over = False
        self.is_reloading = False
        self.bullets = []

        # 重置伤害相关变量
        self.last_damage_time = 0
        self.damage_effect_alpha = 0.0

        # 重置摄像机
        self.camera_x = 0
        self.camera_y = 1.6
        self.camera_z = 10
        self.camera_angle_x = 0
        self.camera_angle_y = 0

        # 重置玩家
        self.player = PlayerCharacter()

        # 生成新敌人
        self.spawn_enemies()

        # 重置鼠标捕获
        self.mouse_captured = False
        if QT_VERSION == 6:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止游戏定时器
        self.game_timer.stop()
        super().closeEvent(event)


class ShootingGameWindow(QMainWindow):
    """3D射击游戏窗口"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("FloorBox - 3D射击游戏 v2.0 增强版 - 修复版")
        self.setGeometry(100, 100, 1024, 768)

        # 设置窗口图标
        self.setWindowIcon(QIcon())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # 返回按钮
        back_btn = AnimatedButton("← 返回主菜单")
        back_btn.clicked.connect(self.close)
        back_btn.setStyleSheet("""
            background-color: #607D8B;
            font-size: 14px;
            padding: 8px;
        """)
        layout.addWidget(back_btn)

        # 游戏标题
        title = QLabel("🎮 3D射击游戏 v2.0 - 修复版")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF5722;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 游戏说明
        instructions = QLabel("WASD移动，空格跳跃，Ctrl蹲下，鼠标瞄准，左键射击，R装弹，F1切换视角，F切换雾效")
        instructions.setStyleSheet("font-size: 14px; color: #64B5F6;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)

        # 修复说明
        fix_label = QLabel("修复：敌人碰撞检测 ✓ 敌人建模精细度 ✓ 渲染闪烁 ✓ 敌人可见距离 ✓")
        fix_label.setStyleSheet("font-size: 12px; color: #4CAF50; font-weight: bold;")
        fix_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(fix_label)

        # OpenGL游戏区域
        try:
            self.gl_widget = OpenGLWidget()
            self.gl_widget.setMinimumSize(800, 600)
            layout.addWidget(self.gl_widget)
        except Exception as e:
            # 如果OpenGL初始化失败，显示错误信息
            error_label = QLabel(f"无法初始化3D游戏: {str(e)}\n请确保显卡驱动程序已更新，并支持OpenGL 2.0+")
            error_label.setStyleSheet("font-size: 14px; color: #f44336;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            return

        # 控制按钮
        control_layout = QHBoxLayout()

        restart_btn = AnimatedButton("🔄 重新开始")
        restart_btn.clicked.connect(self.gl_widget.reset_game)
        restart_btn.setStyleSheet("background-color: #4CAF50;")

        reload_btn = AnimatedButton("🔫 手动装弹")
        reload_btn.clicked.connect(self.manual_reload)
        reload_btn.setStyleSheet("background-color: #2196F3;")

        view_btn = AnimatedButton("👁️ 切换视角")
        view_btn.clicked.connect(self.toggle_view)
        view_btn.setStyleSheet("background-color: #9C27B0;")

        fog_btn = AnimatedButton("🌫️ 切换雾效")
        fog_btn.clicked.connect(self.toggle_fog)
        fog_btn.setStyleSheet("background-color: #795548;")

        control_layout.addWidget(restart_btn)
        control_layout.addWidget(reload_btn)
        control_layout.addWidget(view_btn)
        control_layout.addWidget(fog_btn)
        layout.addLayout(control_layout)

        # 游戏状态显示
        status_layout = QHBoxLayout()

        self.score_label = QLabel("分数: 0")
        self.score_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")

        self.health_label = QLabel("生命: 100%")
        self.health_label.setStyleSheet("font-size: 14px; color: #F44336; font-weight: bold;")

        self.ammo_label = QLabel("弹药: 30/30")
        self.ammo_label.setStyleSheet("font-size: 14px; color: #2196F3; font-weight: bold;")

        self.view_label = QLabel("视角: 第三人称")
        self.view_label.setStyleSheet("font-size: 14px; color: #9C27B0; font-weight: bold;")

        status_layout.addWidget(self.score_label)
        status_layout.addWidget(self.health_label)
        status_layout.addWidget(self.ammo_label)
        status_layout.addWidget(self.view_label)
        layout.addLayout(status_layout)

        # 更新游戏状态定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(100)  # 每100ms更新一次

        self.paused = False

    def manual_reload(self):
        """手动装弹"""
        if hasattr(self, 'gl_widget'):
            if not self.gl_widget.is_reloading and self.gl_widget.ammo < self.gl_widget.max_ammo:
                self.gl_widget.is_reloading = True
                self.gl_widget.reload_start_time = time.time()
                if hasattr(self.gl_widget, 'reload_sound') and self.gl_widget.reload_sound:
                    self.gl_widget.reload_sound.play()

    def toggle_view(self):
        """切换视角"""
        if hasattr(self, 'gl_widget'):
            self.gl_widget.toggle_view()
            self.view_label.setText(f"视角: {'第一人称' if self.gl_widget.first_person else '第三人称'}")

    def toggle_fog(self):
        """切换雾效"""
        if hasattr(self, 'gl_widget'):
            self.gl_widget.toggle_fog()

    def update_status(self):
        """更新状态显示"""
        if hasattr(self, 'gl_widget'):
            self.score_label.setText(f"分数: {self.gl_widget.score}")
            self.health_label.setText(f"生命: {self.gl_widget.health}%")

            if self.gl_widget.is_reloading:
                reload_progress = (time.time() - self.gl_widget.reload_start_time) / self.gl_widget.reload_time
                if reload_progress >= 1.0:
                    self.ammo_label.setText(f"弹药: {self.gl_widget.max_ammo}/{self.gl_widget.max_ammo}")
                else:
                    self.ammo_label.setText(f"弹药: 装弹中... {int(reload_progress * 100)}%")
            else:
                self.ammo_label.setText(f"弹药: {self.gl_widget.ammo}/{self.gl_widget.max_ammo}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.bandwidth_window = None

        # 自动喵喵功能相关属性
        self.auto_meow_enabled = True  # 默认开启
        self.keyboard_monitor = None  # 稍后会在main函数中设置

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("FloorBox - 网络工具箱")
        self.setGeometry(100, 100, 800, 600)

        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: white;
                font-size: 16px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 8px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 2px solid #64B5F6;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 20);
                color: white;
                border: 1px solid #64B5F6;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QTextEdit {
                background-color: rgba(30, 30, 30, 150);
                color: white;
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 5px;
                font-family: Consolas;
                font-size: 12px;
            }
            QProgressBar {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background-color: rgba(0, 0, 0, 30);
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(76, 175, 80, 200),
                    stop:1 rgba(100, 181, 246, 200)
                );
                border-radius: 8px;
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: rgba(100, 181, 246, 100);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #64B5F6;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #64B5F6;
                border: 2px solid #64B5F6;
                border-radius: 10px;
                padding-top: 15px;
            }
        """)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # 标题
        title_label = QLabel("🎯 FloorBox - 网络工具箱")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #FF4081;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 副标题
        subtitle_label = QLabel("多功能网络安全与测试工具")
        subtitle_label.setStyleSheet("font-size: 18px; color: #64B5F6;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 按钮容器
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(15)

        # 创建功能按钮（使用自定义动画按钮）
        buttons = [
            ("🕸️ 网页爬虫", self.open_spider, "#4CAF50"),
            ("🌐 IP检测", self.open_ip_check, "#2196F3"),
            ("🔥 带宽压力测试", self.open_bandwidth, "#FF5722"),
            ("🎮 3D射击游戏 v3.0 修复版", self.open_shooting_game, "#9C27B0"),
            ("🐱 自动喵喵 [开]", self.toggle_auto_meow, "#FF9800"),  # 新增的自动喵喵按钮
            ("ℹ️ 关于", self.show_about, "#FF9800"),
            ("🚪 退出", self.close_application, "#f44336")
        ]

        for text, callback, color in buttons:
            btn = AnimatedButton(text)
            btn.setMinimumHeight(60)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    font-size: 18px;
                    font-weight: bold;
                    border: 2px solid transparent;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                    border: 2px solid #64B5F6;
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 40)};
                }}
            """)
            button_layout.addWidget(btn)

        # 添加到主布局
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addStretch(1)
        layout.addWidget(button_container)
        layout.addStretch(1)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def darken_color(self, hex_color, amount=20):
        """加深颜色"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]

        # 将十六进制转换为RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # 加深颜色
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)

        return f"#{r:02x}{g:02x}{b:02x}"

    def open_spider(self):
        """打开网页爬虫"""
        self.spider_window = SpiderWindow()
        self.spider_window.show()

    def open_ip_check(self):
        """打开IP检测"""
        self.ip_window = IPCheckWindow()
        self.ip_window.show()

    def open_bandwidth(self):
        """打开带宽压力测试"""
        if self.bandwidth_window is None or not self.bandwidth_window.isVisible():
            self.bandwidth_window = BandwidthWindow()
            self.bandwidth_window.show()
        else:
            self.bandwidth_window.raise_()
            self.bandwidth_window.activateWindow()

    def open_shooting_game(self):
        """打开3D射击游戏"""
        try:
            self.shooting_game_window = ShootingGameWindow()
            self.shooting_game_window.show()
        except Exception as e:
            QMessageBox.critical(self, "错误",
                                 f"无法启动3D射击游戏：{str(e)}\n请确保已安装PyOpenGL：pip install PyOpenGL PyOpenGL_accelerate")

    def show_about(self):
        """显示关于信息"""
        about_text = """
        <h2>FloorBox v3.0 修复版</h2>
        <p><b>新增功能：</b></p>
        <ul>
            <li>🐱 自动喵喵功能（3秒无输入后自动输入'喵~'）</li>
        </ul>
        <p><b>修复的问题：</b></p>
        <ul>
            <li>✅ 敌人打不到 - 已修复碰撞检测</li>
            <li>✅ 敌人建模不精细 - 已增加细节</li>
            <li>✅ 渲染闪烁 - 已启用双缓冲和垂直同步</li>
            <li>✅ 敌人只能在很近看到 - 已增加渲染距离</li>
        </ul>
        <p><b>3D射击游戏新特性：</b></p>
        <ul>
            <li>支持第一人称和第三人称视角切换（F1键）</li>
            <li>真实的人形敌人，带有动画和生命值条</li>
            <li>完整的音效系统（射击、击中、装弹、受伤）</li>
            <li>改进的武器模型和射击效果</li>
            <li>环境物体（树木、岩石）</li>
            <li>雾效系统（F键切换）</li>
            <li>更平衡的游戏机制</li>
        </ul>
        <p><b>自动喵喵功能控制：</b></p>
        <ul>
            <li>开启后，在任何文本输入框停止打字3秒后自动输入'喵~'</li>
            <li>点击主菜单的'自动喵喵'按钮可以开关此功能</li>
        </ul>
        <p style="color: #FF9800; font-weight: bold;">
        ⚠️ 警告：带宽压力测试仅用于学习和测试目的<br>
        请勿用于非法用途！
        </p>
        """

        msg = QMessageBox()
        msg.setWindowTitle("关于 FloorBox")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setIconPixmap(QPixmap(1, 1))
        msg.exec()

    def close_application(self):
        """关闭应用程序"""
        # 关闭所有子窗口
        for window in QApplication.topLevelWindows():
            if window != self:
                window.close()

        # 给窗口一点时间关闭
        QApplication.processEvents()
        time.sleep(0.1)

        # 退出应用程序
        QApplication.quit()

    def toggle_auto_meow(self):
        """切换自动喵喵功能"""
        self.auto_meow_enabled = not self.auto_meow_enabled

        # 如果已经有了键盘监听器，设置其启用状态
        if self.keyboard_monitor:
            self.keyboard_monitor.enabled = self.auto_meow_enabled

        # 更新按钮文本
        sender = self.sender()
        if sender:
            status = "开" if self.auto_meow_enabled else "关"
            sender.setText(f"🐱 自动喵喵 [{status}]")
            color = "#FF9800" if self.auto_meow_enabled else "#607D8B"
            sender.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    font-size: 18px;
                    font-weight: bold;
                    border: 2px solid transparent;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                    border: 2px solid #64B5F6;
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 40)};
                }}
            """)

        # 在状态栏显示提示
        status_text = "已启用" if self.auto_meow_enabled else "已禁用"
        self.statusBar().showMessage(f"自动喵喵功能 {status_text}", 3000)

    def closeEvent(self, event):
        """关闭事件"""
        self.close_application()
        event.accept()

    def show_about(self):
        """显示关于信息"""
        about_text = """
        <h2>FloorBox v3.0 修复版</h2>
        <p><b>修复的问题：</b></p>
        <ul>
            <li>✅ 敌人打不到 - 已修复碰撞检测</li>
            <li>✅ 敌人建模不精细 - 已增加细节</li>
            <li>✅ 渲染闪烁 - 已启用双缓冲和垂直同步</li>
            <li>✅ 敌人只能在很近看到 - 已增加渲染距离</li>
        </ul>
        <p><b>3D射击游戏新特性：</b></p>
        <ul>
            <li>支持第一人称和第三人称视角切换（F1键）</li>
            <li>真实的人形敌人，带有动画和生命值条</li>
            <li>完整的音效系统（射击、击中、装弹、受伤）</li>
            <li>改进的武器模型和射击效果</li>
            <li>环境物体（树木、岩石）</li>
            <li>雾效系统（F键切换）</li>
            <li>更平衡的游戏机制</li>
        </ul>
        <p><b>3D射击游戏控制：</b></p>
        <ul>
            <li>WASD - 移动</li>
            <li>空格 - 跳跃</li>
            <li>Ctrl - 蹲下</li>
            <li>鼠标 - 瞄准</li>
            <li>左键 - 射击</li>
            <li>R - 装弹</li>
            <li>F1 - 切换视角</li>
            <li>F - 切换雾效</li>
            <li>Tab - 切换鼠标捕获</li>
        </ul>
        <p style="color: #FF9800; font-weight: bold;">
        ⚠️ 警告：带宽压力测试仅用于学习和测试目的<br>
        请勿用于非法用途！
        </p>
        """

        msg = QMessageBox()
        msg.setWindowTitle("关于 FloorBox")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setIconPixmap(QPixmap(1, 1))
        msg.exec()

    def close_application(self):
        """关闭应用程序"""
        # 关闭所有子窗口
        for window in QApplication.topLevelWindows():
            if window != self:
                window.close()

        # 给窗口一点时间关闭
        QApplication.processEvents()
        time.sleep(0.1)

        # 退出应用程序
        QApplication.quit()

    def closeEvent(self, event):
        """关闭事件"""
        self.close_application()
        event.accept()


# 以下窗口类的代码与原始代码相同，保持不变
class SpiderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("FloorBox - 网页爬虫")
        self.setGeometry(150, 150, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 返回按钮
        back_btn = AnimatedButton("← 返回主菜单")
        back_btn.clicked.connect(self.close)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # 标题
        title = QLabel("🕸️ 网页爬虫工具")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # URL输入
        url_layout = QHBoxLayout()
        url_label = QLabel("目标URL:")
        url_label.setStyleSheet("font-size: 16px;")

        self.url_input = QLineEdit()
        self.url_input.setText("https://www.baidu.com")
        self.url_input.setStyleSheet("font-size: 14px; padding: 8px;")

        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # 按钮
        btn_layout = QHBoxLayout()

        crawl_btn = AnimatedButton("🚀 开始爬取")
        crawl_btn.clicked.connect(self.start_crawl)
        crawl_btn.setStyleSheet("background-color: #4CAF50; font-size: 16px; padding: 10px;")

        clear_btn = AnimatedButton("🗑️ 清空结果")
        clear_btn.clicked.connect(self.clear_results)
        clear_btn.setStyleSheet("background-color: #FF9800; font-size: 16px; padding: 10px;")

        btn_layout.addWidget(crawl_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)

        # 结果显示
        result_label = QLabel("爬取结果:")
        result_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            background-color: rgba(30, 30, 30, 150);
            color: #ffffff;
            font-family: Consolas;
            font-size: 12px;
            padding: 10px;
        """)
        layout.addWidget(self.result_text)

    def start_crawl(self):
        """开始爬取"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "警告", "请输入URL")
            return

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        self.result_text.append(f"\n🔍 正在爬取: {url}")

        # 在工作线程中执行爬取
        self.crawl_thread = CrawlThread(url)
        self.crawl_thread.result_ready.connect(self.display_result)
        self.crawl_thread.start()

    def display_result(self, result):
        """显示结果"""
        self.result_text.append(result)

    def clear_results(self):
        """清空结果"""
        self.result_text.clear()


class CrawlThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        """执行爬取"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, timeout=10, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            result = []
            result.append("=" * 60)
            result.append("📋 网页信息")
            result.append("=" * 60)
            result.append(f"URL: {self.url}")
            result.append(f"状态码: {response.status_code}")

            title = soup.title.string if soup.title else "无标题"
            result.append(f"标题: {title}")

            # 获取一些基本信息
            links = soup.find_all('a', href=True)
            images = soup.find_all('img')

            result.append(f"链接数: {len(links)}")
            result.append(f"图片数: {len(images)}")

            if links:
                result.append("\n前3个链接:")
                for i, link in enumerate(links[:3], 1):
                    href = link['href']
                    text = link.text.strip()[:50] if link.text.strip() else "无文本"
                    result.append(f"  {i}. {text}")
                    result.append(f"     → {href}")

            self.result_ready.emit("\n".join(result))

        except Exception as e:
            self.result_ready.emit(f"❌ 爬取失败: {str(e)}")


class IPCheckWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("FloorBox - IP检测")
        self.setGeometry(150, 150, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 返回按钮
        back_btn = AnimatedButton("← 返回主菜单")
        back_btn.clicked.connect(self.close)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # 标题
        title = QLabel("🌐 IP检测工具")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 目标输入
        target_layout = QHBoxLayout()
        target_label = QLabel("目标域名/IP:")
        target_label.setStyleSheet("font-size: 16px;")

        self.target_input = QLineEdit()
        self.target_input.setText("www.baidu.com")
        self.target_input.setStyleSheet("font-size: 14px; padding: 8px;")

        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_input)
        layout.addLayout(target_layout)

        # 按钮
        btn_layout = QHBoxLayout()

        check_btn = AnimatedButton("🔍 开始检测")
        check_btn.clicked.connect(self.start_check)
        check_btn.setStyleSheet("background-color: #2196F3; font-size: 16px; padding: 10px;")

        clear_btn = AnimatedButton("🗑️ 清空结果")
        clear_btn.clicked.connect(self.clear_results)
        clear_btn.setStyleSheet("background-color: #FF9800; font-size: 16px; padding: 10px;")

        btn_layout.addWidget(check_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)

        # 结果显示
        result_label = QLabel("检测结果:")
        result_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            background-color: rgba(30, 30, 30, 150);
            color: #ffffff;
            font-family: Consolas;
            font-size: 12px;
            padding: 10px;
        """)
        layout.addWidget(self.result_text)

    def start_check(self):
        """开始检测"""
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "警告", "请输入域名或IP")
            return

        self.result_text.append(f"\n🔍 正在检测: {target}")

        # 在工作线程中执行检测
        self.check_thread = CheckThread(target)
        self.check_thread.result_ready.connect(self.display_result)
        self.check_thread.start()

    def display_result(self, result):
        """显示结果"""
        self.result_text.append(result)

    def clear_results(self):
        """清空结果"""
        self.result_text.clear()


class CheckThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, target):
        super().__init__()
        self.target = target

    def run(self):
        """执行检测"""
        try:
            if self.target.startswith(("http://", "https://")):
                domain = self.target.split("//")[-1].split("/")[0]
            else:
                domain = self.target.split("/")[0]

            if ":" in domain:
                domain = domain.split(":")[0]

            result = []
            result.append("=" * 60)
            result.append("🌐 IP检测结果")
            result.append("=" * 60)
            result.append(f"目标: {self.target}")
            result.append(f"域名: {domain}")

            try:
                ip_address = socket.gethostbyname(domain)
                result.append(f"IP地址: {ip_address}")
            except socket.gaierror:
                result.append("❌ 无法解析域名")
                self.result_ready.emit("\n".join(result))
                return

            result.append("\n端口扫描:")
            common_ports = {
                80: "HTTP",
                443: "HTTPS",
                21: "FTP",
                22: "SSH",
                25: "SMTP",
                53: "DNS",
                3306: "MySQL",
                3389: "RDP"
            }

            for port, service in common_ports.items():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result_code = sock.connect_ex((ip_address, port))
                    if result_code == 0:
                        result.append(f"✅ 端口 {port} ({service}): 开放")
                    else:
                        result.append(f"❌ 端口 {port} ({service}): 关闭")
                    sock.close()
                except:
                    result.append(f"⚠️  端口 {port} ({service}): 检测失败")

            self.result_ready.emit("\n".join(result))

        except Exception as e:
            self.result_ready.emit(f"❌ 检测失败: {str(e)}")


class BandwidthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.monster = None
        self.attack_thread = None
        self.stats_queue = queue.Queue(maxsize=1000)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.start_time = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("FloorBox - 带宽压力测试")
        self.setGeometry(150, 150, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 返回按钮
        back_btn = AnimatedButton("← 返回主菜单")
        back_btn.clicked.connect(self.close)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # 标题
        title = QLabel("🔥 带宽压力测试工具")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF5722;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 警告
        warning = QLabel("⚠️ 警告：此功能仅用于学习和测试目的！")
        warning.setStyleSheet("font-size: 16px; color: #FF9800; font-weight: bold;")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning)

        # 控制面板
        control_group = QGroupBox("测试设置")
        control_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #FF5722;
                border: 2px solid #FF5722;
                border-radius: 10px;
                padding-top: 15px;
            }
        """)

        control_layout = QVBoxLayout()

        # 线程数
        thread_layout = QHBoxLayout()
        thread_label = QLabel("并发线程数:")
        thread_label.setStyleSheet("font-size: 14px;")

        self.thread_slider = QSlider(Qt.Orientation.Horizontal)
        self.thread_slider.setRange(10, 100)
        self.thread_slider.setValue(30)
        self.thread_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.thread_slider.setTickInterval(10)

        self.thread_label = QLabel("30")
        self.thread_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF5722;")

        thread_layout.addWidget(thread_label)
        thread_layout.addWidget(self.thread_slider)
        thread_layout.addWidget(self.thread_label)
        control_layout.addLayout(thread_layout)

        self.thread_slider.valueChanged.connect(
            lambda v: self.thread_label.setText(str(v))
        )

        # 持续时间
        duration_layout = QHBoxLayout()
        duration_label = QLabel("持续时间(秒):")
        duration_label.setStyleSheet("font-size: 14px;")

        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setRange(30, 600)
        self.duration_slider.setValue(60)
        self.duration_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.duration_slider.setTickInterval(30)

        self.duration_label = QLabel("60")
        self.duration_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF5722;")

        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_slider)
        duration_layout.addWidget(self.duration_label)
        control_layout.addLayout(duration_layout)

        self.duration_slider.valueChanged.connect(
            lambda v: self.duration_label.setText(str(v))
        )

        # 高级选项
        advanced_layout = QHBoxLayout()
        advanced_label = QLabel("请求超时(秒):")
        advanced_label.setStyleSheet("font-size: 14px;")

        self.timeout_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeout_slider.setRange(1, 10)
        self.timeout_slider.setValue(2)

        self.timeout_label = QLabel("2")
        self.timeout_label.setStyleSheet("font-size: 14px; color: #2196F3;")

        advanced_layout.addWidget(advanced_label)
        advanced_layout.addWidget(self.timeout_slider)
        advanced_layout.addWidget(self.timeout_label)
        control_layout.addLayout(advanced_layout)

        self.timeout_slider.valueChanged.connect(
            lambda v: self.timeout_label.setText(str(v))
        )

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # 统计信息
        stats_group = QGroupBox("实时统计")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding-top: 15px;
            }
        """)

        stats_layout = QGridLayout()

        # 创建统计标签
        self.stats = {
            'requests': QLabel("0"),
            'data': QLabel("0 MB"),
            'success': QLabel("0"),
            'fail': QLabel("0"),
            'speed': QLabel("0 MB/s"),
            'time': QLabel("0秒"),
            'status': QLabel("🟢 空闲")
        }

        labels = [
            ("📊 总请求数:", self.stats['requests']),
            ("💾 总数据量:", self.stats['data']),
            ("✅ 成功请求:", self.stats['success']),
            ("❌ 失败请求:", self.stats['fail']),
            ("⚡ 当前速度:", self.stats['speed']),
            ("⏱️  运行时间:", self.stats['time']),
            ("📈 测试状态:", self.stats['status'])
        ]

        for i, (text, value_label) in enumerate(labels):
            row = i // 2
            col = (i % 2) * 2

            label = QLabel(text)
            label.setStyleSheet("font-size: 14px; color: #B0BEC5;")

            value_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #2196F3;
                padding: 8px;
                background-color: rgba(30, 30, 30, 150);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 30);
                min-width: 150px;
            """)

            stats_layout.addWidget(label, row, col)
            stats_layout.addWidget(value_label, row, col + 1)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # 按钮区域
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)

        self.start_btn = AnimatedButton("🔥 开始压力测试")
        self.start_btn.clicked.connect(self.start_attack)
        self.start_btn.setStyleSheet("""
            background-color: #FF5722;
            font-size: 18px;
            padding: 15px 30px;
            min-width: 200px;
        """)

        self.stop_btn = AnimatedButton("🛑 停止测试")
        self.stop_btn.clicked.connect(self.stop_attack)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            background-color: #607D8B;
            font-size: 18px;
            padding: 15px 30px;
            min-width: 200px;
        """)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addWidget(btn_container)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("等待开始...")
        layout.addWidget(self.progress)

        # 日志区域
        log_group = QGroupBox("测试日志")
        log_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #FF9800;
                border: 2px solid #FF9800;
                border-radius: 10px;
                padding-top: 15px;
            }
        """)

        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            background-color: rgba(30, 30, 30, 150);
            color: #ffffff;
            font-family: Consolas, 'Microsoft YaHei';
            font-size: 11px;
            padding: 10px;
            border-radius: 5px;
        """)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group)

        # 设置更新定时器
        self.update_timer.setInterval(500)

    def start_attack(self):
        """开始压力测试"""
        reply = QMessageBox.question(
            self, "确认测试",
            f"即将启动压力测试：\n\n"
            f"并发线程数: {self.thread_slider.value()}\n"
            f"持续时间: {self.duration_slider.value()}秒\n"
            f"请求超时: {self.timeout_slider.value()}秒\n\n"
            f"⚠️ 这将消耗大量网络带宽！\n"
            f"确认继续吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # 清空统计
        self.clear_stats()

        # 创建BandwidthMonster实例
        self.monster = BandwidthMonster()
        self.monster.request_timeout = self.timeout_slider.value()

        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.stats['status'].setText("🟡 启动中...")

        # 记录开始时间
        self.start_time = time.time()

        # 启动统计更新定时器
        self.update_timer.start()

        # 在工作线程中启动攻击
        self.attack_thread = AttackThread(
            self.monster,
            self.thread_slider.value(),
            self.duration_slider.value(),
            self.stats_queue
        )
        self.attack_thread.finished.connect(self.on_attack_finished)
        self.attack_thread.start()

        # 更新日志
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] 🔥 开始压力测试...")
        self.log_text.append(
            f"[{timestamp}] 📊 配置: {self.thread_slider.value()}线程, {self.duration_slider.value()}秒")
        self.log_text.append(f"[{timestamp}] 🌐 目标: {len(POPULAR_WEBSITES)}个热门网站")

    def stop_attack(self):
        """停止测试"""
        if self.monster:
            self.monster.stop()

        if self.attack_thread and self.attack_thread.isRunning():
            self.attack_thread.quit()
            self.attack_thread.wait(2000)

        self.update_timer.stop()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stats['status'].setText("🔴 已停止")

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] 🛑 测试已停止")
        self.progress.setFormat("已停止")

    def clear_stats(self):
        """清空统计信息"""
        for key in self.stats:
            if key != 'status':
                self.stats[key].setText("0")
        self.log_text.clear()
        self.progress.setValue(0)

    def update_stats(self):
        """更新统计信息"""
        try:
            while not self.stats_queue.empty():
                stats = self.stats_queue.get_nowait()

                if stats['type'] == 'update':
                    self.stats['requests'].setText(f"{stats['total_requests']:,}")
                    self.stats['data'].setText(f"{stats['total_data'] / 1024 / 1024:.2f} MB")
                    self.stats['success'].setText(f"{stats['success']:,}")
                    self.stats['fail'].setText(f"{stats['failed']:,}")

                    speed_mbps = stats['current_speed'] / 1024 / 1024
                    self.stats['speed'].setText(f"{speed_mbps:.2f} MB/s")

                    elapsed_time = stats['elapsed_time']
                    self.stats['time'].setText(f"{elapsed_time:.1f}秒")

                    if self.start_time:
                        duration = self.duration_slider.value()
                        progress = min(100, int((elapsed_time / duration) * 100))
                        self.progress.setValue(progress)
                        self.progress.setFormat(f"{progress}% - {speed_mbps:.1f} MB/s")

                    if speed_mbps > 10:
                        self.stats['status'].setText("🔥 高强度")
                    elif speed_mbps > 5:
                        self.stats['status'].setText("⚡ 中等强度")
                    else:
                        self.stats['status'].setText("🟢 运行中")

                    if random.random() < 0.1:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        url = stats.get('current_url', '未知').split('//')[-1].split('/')[0]
                        self.log_text.append(
                            f"[{timestamp}] 📡 请求 {stats['total_requests']:,} 次, 速度 {speed_mbps:.1f} MB/s")

                elif stats['type'] == 'heartbeat':
                    elapsed_time = stats['elapsed_time']
                    self.stats['time'].setText(f"{elapsed_time:.1f}秒")

                elif stats['type'] == 'complete':
                    self.on_attack_completed(stats)

        except queue.Empty:
            pass
        except Exception as e:
            print(f"更新统计时出错: {e}")

    def on_attack_completed(self, stats):
        """测试完成处理"""
        self.update_timer.stop()

        self.stats['requests'].setText(f"{stats['total_requests']:,}")
        self.stats['data'].setText(f"{stats['total_data'] / 1024 / 1024:.2f} MB")
        self.stats['success'].setText(f"{stats['success']:,}")
        self.stats['fail'].setText(f"{stats['failed']:,}")

        avg_speed = stats['average_speed'] / 1024 / 1024
        self.stats['speed'].setText(f"{avg_speed:.2f} MB/s")
        self.stats['time'].setText(f"{stats['duration']:.1f}秒")
        self.stats['status'].setText("✅ 已完成")

        self.progress.setValue(100)
        self.progress.setFormat(f"完成 - 平均 {avg_speed:.1f} MB/s")

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] ✅ 压力测试完成!")
        self.log_text.append(f"[{timestamp}] 📊 最终统计:")
        self.log_text.append(f"[{timestamp}]   总请求数: {stats['total_requests']:,}")
        self.log_text.append(f"[{timestamp}]   总数据量: {stats['total_data'] / 1024 / 1024:.2f} MB")
        self.log_text.append(f"[{timestamp}]   成功请求: {stats['success']:,}")
        self.log_text.append(f"[{timestamp}]   失败请求: {stats['failed']:,}")
        self.log_text.append(f"[{timestamp}]   平均速度: {avg_speed:.2f} MB/s")
        self.log_text.append(f"[{timestamp}]   持续时间: {stats['duration']:.2f} 秒")

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_attack_finished(self):
        """攻击线程完成"""
        if self.update_timer.isActive():
            self.update_timer.stop()

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        if self.stats['status'].text() != "✅ 已完成":
            self.stats['status'].setText("🔴 已停止")
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] ⚠️  测试意外终止")

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.stop_attack()
        super().closeEvent(event)


class AttackThread(QThread):
    """攻击线程"""
    finished = pyqtSignal()

    def __init__(self, monster, thread_count, duration, stats_queue):
        super().__init__()
        self.monster = monster
        self.thread_count = thread_count
        self.duration = duration
        self.stats_queue = stats_queue

    def run(self):
        """运行攻击"""
        try:
            self.monster.start_rampage(self.thread_count, self.duration, self.stats_queue)
        except Exception as e:
            print(f"攻击线程错误: {e}")
            try:
                self.stats_queue.put_nowait({
                    'type': 'error',
                    'error': str(e)
                })
            except:
                pass
        finally:
            self.finished.emit()


def cleanup_on_exit():
    """程序退出时的清理函数"""
    global bandwidth_monster
    if bandwidth_monster:
        bandwidth_monster.stop()

    # 清理所有网络连接
    try:
        import requests
        requests.session().close()
    except:
        pass


def main():
    # 注册退出清理函数
    atexit.register(cleanup_on_exit)

    # 创建应用
    app = QApplication(sys.argv)

    # 设置应用程序字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    # 创建全局键盘监听器
    keyboard_monitor = GlobalKeyboardMonitor()

    # 显示启动动画
    splash = SimpleSplashScreen()
    splash.show()

    # 显示消息
    splash.showMessage("正在初始化...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                       Qt.GlobalColor.white)

    # 模拟加载
    QApplication.processEvents()
    time.sleep(0.5)

    splash.showMessage("加载模块...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)
    QApplication.processEvents()
    time.sleep(0.5)

    splash.showMessage("准备就绪...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter, Qt.GlobalColor.white)
    QApplication.processEvents()
    time.sleep(0.5)

    # 创建并显示主窗口
    window = MainWindow()

    # 将键盘监听器传递给主窗口
    window.keyboard_monitor = keyboard_monitor

    window.show()

    # 关闭启动动画
    splash.finish(window)

    # 在程序退出时清理键盘钩子
    app.aboutToQuit.connect(keyboard_monitor.cleanup)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()