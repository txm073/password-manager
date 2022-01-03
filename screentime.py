import os, sys, time, json, re
import psutil, win32process, win32gui
import webbrowser

def get_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def get_app(browser_tabs=True):
    pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
    active = psutil.Process(pid[1]).name()
    name = str(active).replace(".exe", "").capitalize()
    title = get_title()
    if "visual studio code" in title.lower():
        return "VSCode"
    if name.lower().strip() not in title.lower().strip() and name != "Explorer":
        name = title
    if name.startswith("Firefox") and browser_tabs:
        tab = win32gui.GetWindowText(
            win32gui.GetForegroundWindow()
        ).split("—")[0].strip()
        if re.search(r"\(\d*\)", tab):
            tab = " ".join(tab.split()[1:])
        name += f": {tab}"
    elif name == "Task Switching":
        return None
    elif "ExperienceHost" in name:
        return None
    return name

def update_file(_dict):
    with open("screentime.json", "w") as f:
        json.dump(_dict, f, indent=4, ensure_ascii=True)

def convert_from_seconds(secs):
    if type(secs) is str:
        return secs
    mins, seconds = divmod(secs, 60)
    if secs < 3600:
        return f"{int(mins)} Minutes, {int(seconds)} Seconds"
    hours, mins = divmod(mins, 60)
    return f"{int(hours)} Hours, {int(mins)} Minutes"

def convert_to_seconds(string):
    if type(string) in [int, float]:
        return string
    string = string.replace(",", "")
    if "Hours" in string:
        hours, _, mins, _ = string.split(" ")
        return int(float(hours) * 3600 +  float(mins) * 60) 
    else:
        mins, _, secs, _ = string.split(" ")
        return int(float(mins) * 60 +  float(secs))

app_times = {}
prev = None
init_time = 5
start_time = time.time()
while True:
    try:
        name = get_app(browser_tabs=False)
        if prev != name and name:
            time_spent = time.time() - start_time
            try:
                app_times[name] = convert_from_seconds(
                    convert_to_seconds(app_times[name]) + time_spent
                )
                update_file(app_times)
            except KeyError:
                if time_spent > init_time:
                    app_times[name] = convert_from_seconds(time_spent)
                    update_file(app_times)
            finally:    
                prev = name
                start_time = time.time()
                time_spent = None
    except (ProcessLookupError, ValueError, psutil.NoSuchProcess):
        pass
    except KeyboardInterrupt:
        info = input("Exit? Y/N")
        if info.upper() == "Y":
            break
        else:
            for item in app_times.items():
                print(item)
"""
for key, value in app_times.items():
    app_times[key] = convert_from_seconds(value)
update_file(app_times)
"""