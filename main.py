import tkinter as tk
from tkinter import ttk, filedialog, TclError
import logging
from queue import Queue
import threading
import time
import ctypes  # 导入 ctypes 库
import pyautogui  # 导入 pyautogui 库
import keyboard

logging.basicConfig(level=logging.DEBUG)


# 定义鼠标点击函数
def mouse_click(x, y, button='left'):
    # 移动鼠标到指定位置
    ctypes.windll.user32.SetCursorPos(x, y)

    # 定义鼠标事件常量
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010

    if button == 'left':
        # 左键按下
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        # 左键释放
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    elif button == 'right':
        # 右键按下
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        # 右键释放
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, x, y, 0, 0)


class MouseClickerGUI:
    def __init__(self, master):
        logging.debug("Initializing MouseClickerGUI")
        self.master = master
        master.title("鼠标连点器")
        master.geometry("369x520")  # 设置窗口大小
        master.protocol("WM_DELETE_WINDOW", self.on_closing)  # 绑定窗口关闭事件

        # 绑定 f2 键
        keyboard.add_hotkey('f2', self.find_mouse_coords)
        # 绑定 f3 和 f4 键
        keyboard.add_hotkey('f3', self.start_clicking)
        keyboard.add_hotkey('f4', self.stop_clicking)

        # 创建面板
        self.panel1 = ttk.Frame(master)
        self.panel1.pack(fill=tk.BOTH, expand=True)

        # 提示标签
        self.label_h = self.create_label(self.panel1, "提示：每行代码后要加延时命令,不然速度很快会出错！", 30, 7, 310, 32)

        # 分组框
        self.groupbox1 = self.create_groupbox(master, "鼠标点击的坐标", 19, 102, 326, 53)
        self.groupbox2 = self.create_groupbox(master, "命令储存", 19, 158, 326, 85)
        self.groupbox3 = self.create_groupbox(master, "鼠标每次点击的间隔时间", 189, 43, 156, 56)
        self.groupbox4 = self.create_groupbox(master, "点击模式", 19, 243, 326, 88)
        self.groupbox5 = self.create_groupbox(master, "鼠标操作", 19, 43, 161, 56)

        # 超级列表框
        self.treeview = ttk.Treeview(self.panel1, columns=("NO", "执行命令", "执行状态"), show="headings")
        self.treeview.heading("NO", text="NO")
        self.treeview.heading("执行命令", text="执行命令")
        self.treeview.heading("执行状态", text="执行状态")
        self.treeview.column("NO", width=50)
        self.treeview.column("执行命令", width=200)
        self.treeview.column("执行状态", width=60)
        self.treeview.place(x=19, y=341, width=326, height=115)
        self.treeview.bind("<ButtonRelease-1>", self.on_treeview_click)  # 使用 <ButtonRelease-1> 事件  绑定点击事件

        # 按钮
        self.start_button = self.create_button(master, "开始 F3", self.start_clicking, 183, 470, 75, 30)
        self.stop_button = self.create_button(master, "停止 F4", self.stop_clicking, 268, 470, 75, 30)
        self.load_script_button = self.create_button(master, "读入脚本", self.load_script, 31, 199, 93, 30)
        self.insert_coords_button = self.create_button(master, "插入坐标", self.insert_coordinates, 18, 470, 75, 30)
        self.insert_delay_button = self.create_button(master, "插入延时", self.insert_delay, 100, 470, 75, 30)
        self.save_commands_button = self.create_button(master, "保存命令", self.save_commands, 137, 199, 93, 30)
        self.clear_all_button = self.create_button(master, "全部清除", self.clear_all_commands, 242, 199, 93, 30)
        # 标签
        self.label1 = self.create_label (master, "请先将命令插入列表再保存！", 120, 168, 158, 24)
        self.label_x = self.create_label (master, "X", 120, 126, 12, 24, foreground="darkblue")
        self.label_y = self.create_label (master, "Y", 230, 126, 12, 24, foreground="darkblue")
        self.label_find_coords = self.create_label (master, "坐标寻找 F2:", 42, 126, 76, 24)
        self.label_delay = self.create_label (master, "延时毫秒：", 198, 65, 62, 24)
        self.label_exec_count = self.create_label (master, "执行次数", 184, 280, 56, 24)
        self.label_loop = self.create_label (master, "循环执行", 71, 280, 56, 24)
        self.label_click_type = self.create_label (master, "点击类型", 27, 65, 60, 24)
        # 输入框
        self.entry_x = self.create_entry(master, 135, 128, 80, 20)
        self.entry_y = self.create_entry(master, 250, 128, 80, 20)
        self.entry_delay = self.create_entry(master, 260, 68, 60, 20)
        self.entry_delay.insert(0, "200")  # 设置默认值
        self.entry_exec_count = self.create_entry(master, 244, 282, 80, 20)
        self.entry_exec_count.insert(0, "200")  # 设置默认值

        # 初始化点击状态
        self.clicking = False
        self.command_queue = Queue()
        self.thread = None
        self.mode = 1  # 初始化 mode 属性

        # 单选框变量
        self.radio_var = tk.IntVar(value=2)

        # 单选框 循环执行
        self.radio_loop = ttk.Radiobutton(master, text="循环执行", variable=self.radio_var, value=1)
        self.radio_loop.place(x=53, y=282, width=20, height=20)

        # 单选框 次数循环
        self.radio_count = ttk.Radiobutton(master, text="次数循环", variable=self.radio_var, value=2)
        self.radio_count.place(x=165, y=282, width=20, height=20)

        # 组合框
        self.combobox_click_type = ttk.Combobox(master, values=["左键单击", "左键双击", "右键单击"], width=15, height=3)
        self.combobox_click_type.current(0)  # 默认选中第一个选项
        self.combobox_click_type.bind("<<ComboboxSelected>>", self.combobox_selected)
        self.combobox_click_type.place(x=86, y=66, width=69, height=20)  # 设置位置和大小

    def on_treeview_click(self, event):
        print("Treeview clicked")  # 调试输出
        selected_item = self.treeview.selection()  # 获取选中的项
        if selected_item:  # 检查是否有选中的项
            print(f"Selected item: {selected_item}")  # 调试输出
            self.treeview.delete(selected_item)  # 删除选中的项


            self.label1.config(text="表项已删除！")

    def on_closing(self):
        logging.debug("Closing the application")
        self.stop_clicking()  # 停止点击操作
        if self.thread and self.thread.is_alive():
            self.thread.join()  # 等待线程结束
        self.master.destroy()  # 销毁主窗口

    def create_entry(self, master, x, y, width, height, **kwargs):
        entry = ttk.Entry(master, width=width, **kwargs)
        entry.place(x=x, y=y, width=width, height=height)
        return entry

    def create_button(self, master, text, command, x, y, width, height, **kwargs):
        button = ttk.Button(master, text=text, command=command, **kwargs)
        button.place(x=x, y=y, width=width, height=height)
        return button

    def create_groupbox(self, master, text, x, y, width, height, **kwargs):
        groupbox = ttk.LabelFrame(master, text=text, **kwargs)
        groupbox.place(x=x, y=y, width=width, height=height)
        return groupbox

    def create_label(self, master, text, x, y, width, height, **kwargs):
        label = ttk.Label(master, text=text, **kwargs)
        label.place(x=x, y=y, width=width, height=height)
        return label

    def combobox_selected(self, event):
        selected_item = self.combobox_click_type.get()
        print(f"组合框选中了 {selected_item}")

    def start_clicking(self):
        logging.debug("Starting clicking")
        if not self.clicking:
            self.clicking = True
            logging.debug("Clicking set to True")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.thread = threading.Thread(target=self.process_commands)
            self.thread.start()

    def stop_clicking(self):
        logging.debug("Stopping clicking")
        self.clicking = False
        logging.debug("Clicking set to False")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def parse_coords(self, command_str):
        try:
            # 新的解析逻辑
            x = int(command_str.split("(x:")[1].split("y:")[0])
            y = int(command_str.split("y:")[1].split(")")[0])
            return x, y
        except (IndexError, ValueError):
            logging.error(f"无法解析命令字符串: {command_str}")
            return None, None

    def parse_delay(self, command_str):
        try:
            delay = int(command_str.split("延时（")[1].split("）")[0])
            return delay
        except IndexError:
            logging.error(f"无法解析命令字符串: {command_str}")
            return None

    def process_commands(self):
        loop_mode = self.radio_var.get()
        exec_count = int(self.entry_exec_count.get())

        while self.clicking:
            self.master.update_idletasks()  # 处理事件
            self.clear_statuses()
            for i in range(len(self.treeview.get_children())):
                item = self.treeview.get_children()[i]
                command_str = self.treeview.item(item, "values")[1]
                self.treeview.item(item, values=(i + 1, command_str, "执行中"))
                self.master.update_idletasks()  # 处理事件

                try:
                    if "左键单击" in command_str or "左键双击" in command_str or "右键单击" in command_str:
                        x, y = self.parse_coords(command_str)
                        if x is not None and y is not None:
                            if "左键单击" in command_str:
                                mouse_click(x, y, button='left')
                            elif "左键双击" in command_str:
                                mouse_click(x, y, button='left')
                                mouse_click(x, y, button='left')
                            elif "右键单击" in command_str:
                                mouse_click(x, y, button='right')
                        else:
                            logging.error(f"无效的坐标命令: {command_str}")
                    elif "延时" in command_str:
                        delay = self.parse_delay(command_str)
                        if delay is not None:
                            time.sleep(delay / 1000)
                except Exception as e:
                    logging.error(f"处理命令时发生错误: {e}")

                self.treeview.item(item, values=(i + 1, command_str, "完成"))
                self.master.update_idletasks()  # 处理事件

                if not self.clicking:
                    break

            if loop_mode == 1:  # 无限循环
                continue
            elif loop_mode == 2:  # 有限次数循环
                exec_count -= 1
                if exec_count <= 0:
                    self.stop_clicking()
                    break

    def clear_statuses(self):
        for i in range(len(self.treeview.get_children()) - 1, -1, -1):
            item = self.treeview.get_children()[i]
            command_str = self.treeview.item(item, "values")[1]
            self.treeview.item(item, values=(i + 1, command_str, ""))



    def load_script(self):
        # 使用文件对话框选择文件
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line:
                        self.treeview.insert("", "end", values=(len(self.treeview.get_children()) + 1, line, ""))
            self.label1.config(text="脚本已加载！")

    def find_mouse_coords(self, event=None):
        x, y = pyautogui.position()
        self.entry_x.delete(0, tk.END)
        self.entry_x.insert(0, str(x))
        self.entry_y.delete(0, tk.END)
        self.entry_y.insert(0, str(y))

    def insert_coordinates(self):
        try:
            x = int(self.entry_x.get())
            y = int(self.entry_y.get())
            command = f"左键单击(x:{x}y:{y})"
            self.treeview.insert("", "end", values=(len(self.treeview.get_children()) + 1, command, ""))
            self.label1.config(text="坐标已插入！")
        except ValueError:
            logging.error("请输入有效的坐标值")
            self.label1.config(text="请输入有效的坐标值！")

    def insert_delay(self):
        try:
            delay = int(self.entry_delay.get())
            command = f"延时（{delay}）"
            self.treeview.insert("", "end", values=(len(self.treeview.get_children()) + 1, command, ""))
            self.label1.config(text="延时已插入！")
        except ValueError:
            logging.error("请输入有效的延时值")
            self.label1.config(text="请输入有效的延时值！")

    def save_commands(self):
        # 使用文件对话框选择保存路径
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                for item in self.treeview.get_children():
                    command_str = self.treeview.item(item, "values")[1]
                    file.write(command_str + "\n")
            self.label1.config(text="命令已保存！")

    def clear_all_commands(self):
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        self.label1.config(text="所有命令已清除！")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MouseClickerGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    finally:
        logging.info("程序结束")
        # 禁用失败安全机制
        pyautogui.FAILSAFE = False
