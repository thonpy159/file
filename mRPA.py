import tkinter as tk
import customtkinter
import os
import sys
from pynput import keyboard,mouse
import datetime
import Play_record
import re

width, height = 300, 350
titlename = "mRPA"
headername = "mRPA"

logno = 0
def pp(pp):
    global logno
    if logno < 10:
        logno = str("0")+str(logno)
    print(f"logno_{logno}: {pp}")
    logno = int(logno)
    logno +=1

FONT_TYPE = "meiryo"
class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()
        self.fonts = (FONT_TYPE, 15)
        self.csv_filepath = None
        self.setup_form()
    def setup_form(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.geometry(f"{width}x{height}")
        self.title(f"{titlename}")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.read_file_frame = ReadFileFrame(master=self, header_name=headername)
        self.read_file_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

class ReadFileFrame(customtkinter.CTkFrame):
    def __init__(self, *args, header_name="ReadFileFrame", **kwargs):
        super().__init__(*args, **kwargs)
        self.is_ctrl_pressed = False
        self.mouse_listener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll, on_move=self.on_move)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
        self.output = f"data/record"
        self.start_time = None
        self.escape_listener = keyboard.Listener(on_press=self.escape)
        self.escape_listener.start()
        self.record_list = []
        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        self.get_check = 0
        self.setup_form()
    def setup_form(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.label = customtkinter.CTkLabel(self, text=self.header_name, font=(FONT_TYPE, 11))
        self.label.grid(row=0, column=0, padx=20, sticky="w")
        self.textbox = customtkinter.CTkEntry(master=self, placeholder_text="txtファイルを読み込む", width=50, font=(FONT_TYPE,10))
        self.textbox.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        self.button_select = customtkinter.CTkButton(master=self,
            fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),   # ボタンを白抜きにする
            command=self.button_select_callback, text="ファイル選択", font=self.fonts)
        self.button_select.grid(row=2, column=0, padx=10, pady=(0,10))
        self.button_open = customtkinter.CTkButton(master=self, command=self.latest_file_find, text="最新ファイルを選択", font=self.fonts)
        self.button_open.grid(row=3, column=0, padx=10, pady=(0,10))
        self.button_open = customtkinter.CTkButton(master=self, command=self.record, text="Record", font=self.fonts)
        self.button_open.grid(row=4, column=0, padx=10, pady=(0,10))
        self.button_open = customtkinter.CTkButton(master=self, command=self.record_end, text="Record end", font=self.fonts)
        self.button_open.grid(row=5, column=0, padx=10, pady=(0,10))
        self.button_open = customtkinter.CTkButton(master=self, command=self.Play_record, text="Play Record", font=self.fonts)
        self.button_open.grid(row=6, column=0, padx=10, pady=(0,10))
        self.checkbox = customtkinter.CTkCheckBox(master=self, command=self.mouse_track, text="mouse track", font=self.fonts)
        self.checkbox.grid(row=7, column=0, padx=10, pady=(0,10))

    def button_select_callback(self):
        file_name = ReadFileFrame.file_read()
        if file_name is not None:
            self.textbox.delete(0, tk.END)
            self.textbox.insert(0, file_name)

    def button_open_callback(self):
        file_name = self.textbox.get()
        if file_name is not None or len(file_name) != 0:
            with open(file_name) as f:
                data = f.read()
                print(data)

    @staticmethod
    def file_read():
        current_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = tk.filedialog.askopenfilename(filetypes=[('txtファイル','*.txt')],initialdir=current_dir)
        if len(file_path) != 0:
            return file_path
        else:
            return None
    def latest_file_find(self,folder_path="./data/record/"):
        try:
            folder_fullpath = os.path.abspath(folder_path)
            folders = [f for f in os.listdir(folder_fullpath) if os.path.isdir(os.path.join(folder_fullpath, f))]
            numeric_folders = [f for f in folders if f.isnumeric()]
            if numeric_folders:
                folder_path_specify = os.path.join(folder_path, numeric_folders[0])
                full_path = os.path.join(folder_fullpath,numeric_folders[0])
            files = os.listdir(folder_path_specify)
            files.sort(reverse=True)
            latest_file = os.path.join(full_path, files[0])
            latest_file = latest_file.replace("\\","/")
            file_name = latest_file
            if file_name is not None:
                self.textbox.delete(0, tk.END)
                self.textbox.insert(0, file_name)
        except FileNotFoundError:
            print("指定されたフォルダが存在しません。")

    def record(self):
        if not self.keyboard_listener.is_alive():
            if self.get_check==1:
                self.mouse_listener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll, on_move=self.on_move)
            else:
                self.mouse_listener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll)
            self.keyboard_listener = keyboard.Listener(on_press=self.on_press,on_release=self.on_release)
            self.mouse_listener.start()
            self.keyboard_listener.start()
            self.start_time = datetime.datetime.now()
            print("*** record start ***")
            self.log_create()
            print(f"Recording to file {self.log_filename}")
        else:
            print("*** Recording already in progress ***")
    def record_end(self):
        if self.keyboard_listener.is_alive():
            print("record_end log:",self.record_list)
            line_list_kai = self.changer(self.record_list)
            self.record_list = []
            with open(self.log_filename, 'a') as f:
                for i in line_list_kai:
                    i = i+"\n"
                    f.write(i)
            print(output_filename,"に記録しました。")
            print("*** record end ***")
            self.start_time = None
            self.keyboard_listener.stop()
            self.mouse_listener.stop()
        else:
            print("*** No recording in progress ***")
    def log_create(self):
        i = 0
        global output_filename
        t_delta = datetime.timedelta(hours=9)
        JST = datetime.timezone(t_delta, 'JST')
        now = datetime.datetime.now(JST)
        day = now.strftime('%Y%m%d')
        times = now.strftime('%H%M')
        output_filename = f"{self.output}/{day}/{times}_log{i:04}.txt"
        while True:
            os.makedirs(f"{self.output}/{day}", exist_ok=True)
            self.log_filename = f"{self.output}/{day}/{times}_log{i:04}.txt"
            if os.path.exists(self.log_filename):
                i+=1
                self.log_filename = f"{self.output}/{day}/{times}_log{i:04}.txt"
            else:
                with open(self.log_filename, 'w') as f:
                    f.write(f"Recording started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                break

    def mouse_track(self):
        self.get_check=self.checkbox.get()
        if self.get_check == 1:
            print("mouse track flg on")
        else:
            print("mouse track flg off")

    def on_click(self, x, y, button, pressed):
        if pressed:
            elapsed_time = datetime.datetime.now() - self.start_time
            self.record_list.append(f"Elapsed time: {elapsed_time}")
            self.record_list.append(f"Mouse clicked at ({x}, {y}) with {button} button")
            print(f"Mouse clicked at ({x}, {y}) with {button} button (elapsed time: {elapsed_time})")
        else:
            elapsed_time = datetime.datetime.now() - self.start_time
            self.record_list.append(f"Elapsed time: {elapsed_time}")
            self.record_list.append(f"Mouse released at ({x}, {y}) with {button} button")
            print(f"Mouse clicked at ({x}, {y}) with {button} button (elapsed time: {elapsed_time})")

    def on_scroll(self, x, y, dx, dy):
        print("Mouse scrolled at ({0}, {1})({2}, {3})".format(x, y, dx, dy))
    def on_move(self, x, y):
        self.record_list.append(f"Mouse moved to ({x}, {y})")
        print("Mouse moved to ({0}, {1})".format(x, y))

    def on_press(self, key):
        try:
            if key == keyboard.Key.esc:
                print("StopKey")
                self.stop_monitoring()
                app.destroy()
                return False
            if key == keyboard.Key.enter:
                key = "enter"
                elapsed_time = datetime.datetime.now() - self.start_time
                self.record_list.append(f"Elapsed time: {elapsed_time}")
                self.record_list.append(f"Key {key} pressed")
                print(f"Key {key} pressed (elapsed time: {elapsed_time})")
            if key == keyboard.Key.backspace:
                key = "backspace"
                elapsed_time = datetime.datetime.now() - self.start_time
                self.record_list.append(f"Elapsed time: {elapsed_time}")
                self.record_list.append(f"Key {key} pressed")
                print(f"Key {key} pressed (elapsed time: {elapsed_time})")
            if key == keyboard.Key.space:
                key = "space"
                elapsed_time = datetime.datetime.now() - self.start_time
                self.record_list.append(f"Elapsed time: {elapsed_time}")
                self.record_list.append(f"Key {key} pressed")
                print(f"Key {key} pressed (elapsed time: {elapsed_time})")
            if key.char == '\x03':
                key = "ctrl+c"
                elapsed_time = datetime.datetime.now() - self.start_time
                self.record_list.append(f"Elapsed time: {elapsed_time}")
                self.record_list.append(f"Key {key} pressed")
                print(f"Key {key} pressed (elapsed time: {elapsed_time})")
            if key.char == '\x16':
                key = "ctrl+v"
                elapsed_time = datetime.datetime.now() - self.start_time
                self.record_list.append(f"Elapsed time: {elapsed_time}")
                self.record_list.append(f"Key {key} pressed")
                print(f"Key {key} pressed (elapsed time: {elapsed_time})")
            else:
                elapsed_time = datetime.datetime.now() - self.start_time
                self.record_list.append(f"Elapsed time: {elapsed_time}")
                self.record_list.append(f"Key {key} pressed")
                print(f"Key {key} pressed (elapsed time: {elapsed_time})")
        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.is_ctrl_pressed = False
            else:
                elapsed_time = datetime.datetime.now() - self.start_time
                self.record_list.append(f"Elapsed time: {elapsed_time}")
                self.record_list.append(f"Key {key} released")
                print(f"Key {key} released (elapsed time: {elapsed_time})")
        except AttributeError:
            pass

    def escape(self,key):
        if key == keyboard.Key.esc:
            print('プログラムを終了します')
            self.stop_monitoring()
            app.destroy()
            sys.exit(0)
    def stop_monitoring(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
    def is_monitoring(self):
        return self.keyboard_listener is not None
    def Play_record(self):
        print("************* Play_record start *************")
        try:
            log_file = self.textbox.get()
            print(f"{log_file}を実行します。")
            player = Play_record.Playback(log_file)
            player.play()
            print("************* Play_record end *************")
        except:
            print("ファイルが未選択です。最新ファイルを実行します。")
            log_file = self.latest_file_find()
            print(log_file,"を再生")
            player = Play_record.Playback(log_file)
            player.play()
            print("************* Play_record end *************")
    def latest_file_find(self,folder_path="./data/record/"):
        try:
            folder_fullpath = os.path.abspath(folder_path)
            folders = [f for f in os.listdir(folder_fullpath) if os.path.isdir(os.path.join(folder_fullpath, f))]
            numeric_folders = [f for f in folders if f.isnumeric()]
            if numeric_folders:
                numeric_folders.sort(reverse=True)
                folder_path_specify = os.path.join(folder_path, numeric_folders[0])
                full_path = os.path.join(folder_fullpath,numeric_folders[0])
            files = os.listdir(folder_path_specify)
            files.sort(reverse=True)
            latest_file = os.path.join(full_path, files[0])
            latest_file = latest_file.replace("\\","/")
            self.textbox.delete(0, tk.END)
            self.textbox.insert(0, latest_file)
            return latest_file
        except FileNotFoundError:
            print("指定されたフォルダが存在しません。")

    def changer(self,record_list):
        line_list = []
        record_list.pop()
        record_list.pop()
        line_list = record_list
        pp(line_list)
        mouse_flg=False
        line_list_kai=[]
        elapsed_before,i,click_time = 0*3
        x_temp, y_temp = 0, 0
        while i < len(line_list):
            line = line_list[i]
            if "Elapsed time:" in line:
                match = re.search(r'(\d+:\d+:\d+\.\d+)', line)
                elapsed_time = match.group(1)
                change_elapsed_time = self.sec_change(elapsed_time)
                calc_time = change_elapsed_time - elapsed_before
                if mouse_flg:
                    click_time_before = calc_time
                    click_time = format(click_time_before, '.5f')
                else:
                    calc_time_kai = format(calc_time, '.5f')
                    line_list_kai.append(f"sleep_____: {calc_time_kai}")
                elapsed_before =  change_elapsed_time
            elif "Mouse clicked at" in line:
                coords = line.split("(")[1].split(")")[0].split(", ")
                x_temp, y_temp = int(coords[0]), int(coords[1])
                mouse_flg = True
            elif "Mouse released at" in line:
                coords = line.split("(")[1].split(")")[0].split(", ")
                x, y = int(coords[0]), int(coords[1])
                pattern = r'Button\.(\w+)\sbutton'
                button_serch = re.search(pattern, line)
                button_str = button_serch.group(1)
                if (x == x_temp and y == y_temp) or (x_temp ==0 and y_temp == 0):
                    if button_str=="left":
                        line_list_kai.append(f"click left: {x},{y},{click_time}")
                    else:
                        line_list_kai.append(f"clickright: {x},{y},{click_time}")
                    mouse_flg = False
                else:
                    line_list_kai.append(f"Drag&Drop_: {x_temp},{y_temp},{x},{y},{click_time}")
                    mouse_flg = False

            elif "Key " in line:
                if "press" in line:
                    pattern = '.*? (.*?) pressed'
                    results = re.match(pattern, line)
                    result = results.group(1)
                    line_list_kai.append(f"key__press: {result}")
                elif "relea" in line:
                    pattern = '.*? (.*?) released'
                    results = re.match(pattern, line)
                    result = results.group(1)
                    line_list_kai.append(f"key__relea: {result}")
            elif "Mouse moved to" in line:
                values = [int(x) for x in line.split('(')[1].split(')')[0].split(',')]
                x, y = values[0],values[1]
                line_list_kai.append(f"move______: {x},{y}")
            i +=1
        print("line_list_kai:",line_list_kai)
        return line_list_kai

    def sec_change(self,times):
        times_str=str(times)
        if "-" in str(times):
            times_str_split = times_str.split(' ')[1]
            times_str = times_str_split
        else:
            pass
        t2 = datetime.datetime.strptime(times_str, '%H:%M:%S.%f').time()
        times_changed = (t2.hour * 3600) + (t2.minute * 60) + t2.second + (t2.microsecond / 1000000)
        return times_changed


if __name__ == "__main__":
    print("～～～～～ start ～～～～～")
    app = App()
    try:
        app.mainloop()
        print("～～～～～ end ～～～～～")
    except KeyboardInterrupt:
        print('***** 強制終了 *****')
        sys.exit()