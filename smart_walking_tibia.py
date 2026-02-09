import tkinter as tk
import ctypes
import ctypes.wintypes as wt
import threading
import time
import sys
import os
import json
import gc
gc.disable()

import pystray
from PIL import Image


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL        = 13
WM_KEYDOWN            = 0x0100
WM_KEYUP              = 0x0101
WM_SYSKEYDOWN         = 0x0104
WM_SYSKEYUP           = 0x0105
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001
LLKHF_INJECTED        = 0x00000010

kernel32.GetModuleHandleW.restype  = ctypes.c_void_p
kernel32.GetModuleHandleW.argtypes = [ctypes.c_wchar_p]
kernel32.LoadLibraryW.restype  = ctypes.c_void_p
kernel32.LoadLibraryW.argtypes = [ctypes.c_wchar_p]
kernel32.GetLastError.restype  = wt.DWORD
kernel32.GetLastError.argtypes = []
user32.SetWindowsHookExW.restype  = ctypes.c_void_p
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, wt.DWORD]
user32.CallNextHookEx.restype  = ctypes.c_long
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, wt.WPARAM, wt.LPARAM]
user32.UnhookWindowsHookEx.restype  = wt.BOOL
user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]
user32.GetMessageW.restype  = wt.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(wt.MSG), ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint]
user32.TranslateMessage.argtypes  = [ctypes.POINTER(wt.MSG)]
user32.DispatchMessageW.argtypes  = [ctypes.POINTER(wt.MSG)]
user32.keybd_event.restype  = None
user32.keybd_event.argtypes = [wt.BYTE, wt.BYTE, wt.DWORD, ctypes.c_size_t]
user32.GetForegroundWindow.restype  = ctypes.c_void_p
user32.GetForegroundWindow.argtypes = []
user32.GetClassNameW.restype  = ctypes.c_int
user32.GetClassNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
user32.GetAsyncKeyState.restype  = ctypes.c_short
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetWindowTextW.restype  = ctypes.c_int
user32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
user32.GetWindowTextLengthW.restype  = ctypes.c_int
user32.GetWindowTextLengthW.argtypes = [ctypes.c_void_p]
user32.GetWindowThreadProcessId.restype  = wt.DWORD
user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(wt.DWORD)]
user32.GetWindowRect.restype  = wt.BOOL
user32.GetWindowRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(wt.RECT)]
user32.EnumWindows.restype  = wt.BOOL
user32.EnumWindows.argtypes = [ctypes.c_void_p, ctypes.c_void_p]


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode",      wt.DWORD),
        ("scanCode",    wt.DWORD),
        ("flags",       wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, wt.WPARAM, wt.LPARAM
)

OUTKEY = {
    'up':    (0x26, 0x48, True),
    'down':  (0x28, 0x50, True),
    'left':  (0x25, 0x4B, True),
    'right': (0x27, 0x4D, True),
    'nw':    (0x24, 0x47, False),
    'ne':    (0x21, 0x49, False),
    'sw':    (0x23, 0x4F, False),
    'se':    (0x22, 0x51, False),
}

VK_WASD = {
    0x57: 'up',
    0x41: 'left',
    0x53: 'down',
    0x44: 'right',
    0x51: 'nw',
    0x45: 'ne',
    0x5A: 'sw',
    0x43: 'se',
}
VK_WASD_SET = set(VK_WASD.keys())

VK_ARROWS = {
    0x26: 'up',
    0x28: 'down',
    0x25: 'left',
    0x27: 'right',
}
VK_ARROWS_SET = set(VK_ARROWS.keys())

ARROW_COMBOS = {
    frozenset(['up', 'right']):   'ne',
    frozenset(['up', 'left']):    'nw',
    frozenset(['down', 'right']): 'se',
    frozenset(['down', 'left']):  'sw',
}

VK_NAMES = {
    0x70: "F1",  0x71: "F2",  0x72: "F3",  0x73: "F4",
    0x74: "F5",  0x75: "F6",  0x76: "F7",  0x77: "F8",
    0x78: "F9",  0x79: "F10", 0x7A: "F11", 0x7B: "F12",
    0x14: "CapsLock", 0x90: "NumLock", 0x91: "ScrollLock",
    0x2D: "Insert", 0x2E: "Delete", 0x13: "Pause",
    0xC0: "~",  0xBD: "-",  0xBB: "=",  0xDC: "\\",
    0xDB: "[",  0xDD: "]",  0xBA: ";",  0xDE: "'",
    0xBC: ",",  0xBE: ".",  0xBF: "/",
    0x6A: "Num*", 0x6B: "Num+", 0x6D: "Num-", 0x6E: "Num.",
    0x6F: "Num/", 0x60: "Num0", 0x61: "Num1", 0x62: "Num2",
    0x63: "Num3", 0x64: "Num4", 0x65: "Num5", 0x66: "Num6",
    0x67: "Num7", 0x68: "Num8", 0x69: "Num9",
    0x20: "Space", 0x09: "Tab", 0x1B: "Esc",
}

MODIFIER_VKS = {0x10, 0x11, 0x12, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5}

BLOCKED_HOTKEYS = VK_WASD_SET | VK_ARROWS_SET | {
    0x24, 0x21, 0x23, 0x22,
    0x5B, 0x5C,
    0x0D, 0x08,
}


def vk_to_name(vk):
    if vk in VK_NAMES:
        return VK_NAMES[vk]
    if 0x30 <= vk <= 0x39:
        return chr(vk)
    if 0x41 <= vk <= 0x5A:
        return chr(vk)
    return f"0x{vk:02X}"


def hotkey_combo_name(mods, vk):
    parts = []
    if mods & 0x01:
        parts.append("Ctrl")
    if mods & 0x02:
        parts.append("Shift")
    if mods & 0x04:
        parts.append("Alt")
    parts.append(vk_to_name(vk))
    return "+".join(parts)


def get_current_modifiers():
    mods = 0
    if user32.GetAsyncKeyState(0x11) & 0x8000:
        mods |= 0x01
    if user32.GetAsyncKeyState(0x10) & 0x8000:
        mods |= 0x02
    if user32.GetAsyncKeyState(0x12) & 0x8000:
        mods |= 0x04
    return mods


TIBIA_CLASS_NAMES = {"tibiaclient"}


def is_tibia_focused():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value.lower() in TIBIA_CLASS_NAMES


def find_tibia_hwnd():
    hwnd = user32.GetForegroundWindow()
    if hwnd:
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        if buf.value.lower() in TIBIA_CLASS_NAMES:
            return hwnd
    return None


_CONFIG_FILE = "walkingtools.json"
_save_pending = threading.Event()


def _get_config_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, _CONFIG_FILE)


def _save_config():
    _save_pending.set()


def _do_save_config():
    path = _get_config_path()
    try:
        cfg = {"hotkey_vk": int(hotkey_vk), "hotkey_mods": int(hotkey_mods)}
        data = json.dumps(cfg)
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        _log_queue.append(f"Config saved: {path}")
    except Exception as e:
        _log_queue.append(f"ERROR saving config: {type(e).__name__}: {e}")


def _load_config():
    global hotkey_vk, hotkey_mods
    path = _get_config_path()
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        hotkey_vk = int(cfg.get("hotkey_vk", 0))
        hotkey_mods = int(cfg.get("hotkey_mods", 0))
        _log_queue.append(f"Hotkey loaded: {hotkey_combo_name(hotkey_mods, hotkey_vk) if hotkey_vk else 'none'}")
    except Exception as e:
        _log_queue.append(f"Error loading config: {e}")


def get_tibia_rect():
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    result = []
    def _enum(hwnd, _):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        if buf.value.lower() in TIBIA_CLASS_NAMES:
            rect = wt.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            result.append((rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top))
        return True
    user32.EnumWindows(WNDENUMPROC(_enum), 0)
    return result[0] if result else None


def send_key(direction, up=False):
    vk, sc, ext = OUTKEY[direction]
    flags = 0
    if ext:
        flags |= KEYEVENTF_EXTENDEDKEY
    if up:
        flags |= KEYEVENTF_KEYUP
    user32.keybd_event(vk, sc, flags, 99)


def tap(direction):
    send_key(direction, up=False)
    time.sleep(0.001)
    send_key(direction, up=True)


wasd_enabled  = False
smart_enabled = False
wasd_held  = {}
arrow_held = {}
_log_queue = []
hook_installed = False

hotkey_vk        = 0
hotkey_mods      = 0
hotkey_listening = False
_toggle_event    = threading.Event()
_osd_event_on    = threading.Event()
_osd_event_off   = threading.Event()

_remembered_wasd  = False
_remembered_smart = False
_all_paused       = False


def _install_hook():
    global hook_installed

    def proc(nCode, wParam, lParam):
        global hotkey_listening, hotkey_vk, hotkey_mods

        if nCode < 0:
            return user32.CallNextHookEx(0, nCode, wParam, lParam)

        try:
            kb = ctypes.cast(
                lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)
            ).contents

            if kb.dwExtraInfo == 99:
                return user32.CallNextHookEx(0, nCode, wParam, lParam)
            if kb.flags & LLKHF_INJECTED:
                return user32.CallNextHookEx(0, nCode, wParam, lParam)

            vk = kb.vkCode
            is_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)
            is_up   = wParam in (WM_KEYUP, WM_SYSKEYUP)

            if not (is_down or is_up):
                return user32.CallNextHookEx(0, nCode, wParam, lParam)

            if hotkey_listening and is_down:
                if vk == 0x1B:
                    hotkey_vk = 0
                    hotkey_mods = 0
                    hotkey_listening = False
                    _save_config()
                    _log_queue.append("Hotkey cleared")
                    return 1
                if vk in MODIFIER_VKS:
                    return user32.CallNextHookEx(0, nCode, wParam, lParam)
                if vk not in BLOCKED_HOTKEYS:
                    hotkey_mods = get_current_modifiers()
                    hotkey_vk = vk
                    hotkey_listening = False
                    _save_config()
                    _log_queue.append(f"Hotkey set: {hotkey_combo_name(hotkey_mods, vk)}")
                    return 1
                else:
                    _log_queue.append(f"Blocked key: {vk_to_name(vk)}")
                    return 1

            if hotkey_vk and vk == hotkey_vk and is_down:
                current_mods = get_current_modifiers()
                if current_mods == hotkey_mods:
                    _toggle_event.set()
                    return 1

            if not is_tibia_focused():
                return user32.CallNextHookEx(0, nCode, wParam, lParam)

            if wasd_enabled and vk in VK_WASD_SET:
                wasd_held[vk] = is_down
                return 1

            if smart_enabled and vk in VK_ARROWS_SET:
                arrow_held[vk] = is_down
                return 1

        except Exception:
            pass

        return user32.CallNextHookEx(0, nCode, wParam, lParam)

    hookproc = HOOKPROC(proc)
    _install_hook._ref = hookproc

    def _thread():
        global hook_installed
        python_dll = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
        attempts = [
            ("python dll", lambda: kernel32.LoadLibraryW(python_dll)),
            ("exe handle", lambda: kernel32.GetModuleHandleW(None)),
            ("user32.dll", lambda: kernel32.LoadLibraryW("user32.dll")),
            ("NULL",       lambda: None),
        ]

        handle = None
        for desc, get_hmod in attempts:
            hmod = get_hmod()
            h = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL, hookproc, hmod or 0, 0
            )
            if h:
                handle = h
                _log_queue.append(f"Hook OK via {desc}")
                break
            else:
                err = kernel32.GetLastError()
                _log_queue.append(f"  tried {desc}: error {err}")

        if not handle:
            _log_queue.append("Hook FAILED! Run as Admin.")
            return

        hook_installed = True
        _install_hook._handle = handle
        msg = wt.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    t = threading.Thread(target=_thread, daemon=True)
    t.start()
    time.sleep(0.05)


class OutputThread:
    TICK = 0.001

    def __init__(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while self._running:
            try:
                self._process_wasd()
                self._process_smart()
            except Exception as e:
                _log_queue.append(f"Error: {e}")
            time.sleep(self.TICK)

    def _process_wasd(self):
        if not wasd_enabled:
            return
        if not is_tibia_focused():
            return
        for vk, direction in VK_WASD.items():
            if wasd_held.get(vk, False):
                tap(direction)

    def _process_smart(self):
        if not smart_enabled:
            return
        if not is_tibia_focused():
            return
        held = set()
        for vk, name in VK_ARROWS.items():
            if arrow_held.get(vk, False):
                held.add(name)
        if not held:
            return
        direction = None
        for combo, diag in ARROW_COMBOS.items():
            if combo.issubset(held):
                direction = diag
                break
        if direction is None:
            for a in ('up', 'down', 'left', 'right'):
                if a in held:
                    direction = a
                    break
        if direction:
            tap(direction)

    def stop(self):
        self._running = False


class App:
    BG     = "#1a1a2e"
    ROW_BG = "#16213e"
    RED    = "#c0392b"
    GREEN  = "#27ae60"
    YELLOW = "#f39c12"

    def __init__(self):
        self._build()
        _load_config()
        if hotkey_vk:
            self.hotkey_var.set(hotkey_combo_name(hotkey_mods, hotkey_vk))
        _install_hook()
        self.output = OutputThread()
        self._poll_log()
        self._poll_hotkey()
        self.root.after(100, self._setup_tray)

    def _build(self):
        self.root = tk.Tk()
        self.root.title("Walking Tools")
        self.root.geometry("300x320")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=self.BG)
        self._osd_window = None
        self.tray_icon = None

        icon_path = resource_path("Sorcerer.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)

        tk.Label(
            self.root, text="Walking Tools",
            fg="#e0e0e0", bg=self.BG, font=("Segoe UI", 10, "bold")
        ).pack(pady=(6, 4))

        f1 = tk.Frame(self.root, bg=self.ROW_BG, padx=8, pady=5)
        f1.pack(fill="x", padx=10, pady=2)
        tk.Label(f1, text="WASD + Q E Z C", fg="#ccc", bg=self.ROW_BG,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.wasd_var = tk.StringVar(value="OFF")
        self.wasd_btn = tk.Button(
            f1, textvariable=self.wasd_var, width=8,
            command=self.toggle_wasd,
            bg=self.RED, fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2"
        )
        self.wasd_btn.pack(side="right")

        f2 = tk.Frame(self.root, bg=self.ROW_BG, padx=8, pady=5)
        f2.pack(fill="x", padx=10, pady=2)
        tk.Label(f2, text="Smart Walking (Arrows)", fg="#ccc", bg=self.ROW_BG,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.smart_var = tk.StringVar(value="OFF")
        self.smart_btn = tk.Button(
            f2, textvariable=self.smart_var, width=8,
            command=self.toggle_smart,
            bg=self.RED, fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2"
        )
        self.smart_btn.pack(side="right")

        f3 = tk.Frame(self.root, bg=self.ROW_BG, padx=8, pady=5)
        f3.pack(fill="x", padx=10, pady=2)
        tk.Label(f3, text="Hotkey Toggle", fg="#ccc", bg=self.ROW_BG,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        self.hotkey_var = tk.StringVar(value="None")
        self.hotkey_btn = tk.Button(
            f3, textvariable=self.hotkey_var, width=10,
            command=self._start_hotkey_listen,
            bg="#444", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", cursor="hand2"
        )
        self.hotkey_btn.pack(side="right")

        tk.Label(
            self.root,
            text="WASD: W\u2191 A\u2190 S\u2193 D\u2192 | Q\u2196 E\u2197 Z\u2199 C\u2198\n"
                 "Smart: \u2191+\u2192=\u2197  \u2191+\u2190=\u2196  \u2193+\u2192=\u2198  \u2193+\u2190=\u2199\n"
                 "\u26a1 Only works with Tibia focused",
            fg="#666", bg=self.BG, font=("Segoe UI", 8), justify="center"
        ).pack(pady=(3, 2))

        self.log_text = tk.Text(
            self.root, height=5, width=38,
            bg="#0d0d1a", fg="#aaa", font=("Consolas", 9),
            relief="flat", state="disabled"
        )
        self.log_text.pack(padx=10, pady=(2, 4), fill="x")

        self.root.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)

    def _setup_tray(self):
        icon_path = resource_path("Sorcerer.ico")
        try:
            self._tray_image = Image.open(icon_path)
        except Exception:
            self._tray_image = Image.new('RGB', (64, 64), '#27ae60')

        menu = pystray.Menu(
            pystray.MenuItem("Open", self._tray_show, default=True),
            pystray.MenuItem("Close", self._tray_quit),
        )
        self.tray_icon = pystray.Icon(
            "WalkingTools", self._tray_image, "Walking Tools", menu
        )
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _minimize_to_tray(self):
        self.root.withdraw()

    def _tray_show(self, icon=None, item=None):
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _tray_quit(self, icon=None, item=None):
        self.root.after(0, self._real_close)

    def _start_hotkey_listen(self):
        global hotkey_listening
        if hotkey_listening:
            hotkey_listening = False
            if hotkey_vk:
                self.hotkey_var.set(hotkey_combo_name(hotkey_mods, hotkey_vk))
            else:
                self.hotkey_var.set("None")
            self.hotkey_btn.config(bg="#444")
            return

        hotkey_listening = True
        self.hotkey_var.set("Press...")
        self.hotkey_btn.config(bg=self.YELLOW)
        _log_queue.append("Press combo (e.g. Ctrl+H) | Esc=clear")

    def _poll_hotkey(self):
        if not hotkey_listening and self.hotkey_var.get() == "Press...":
            if hotkey_vk:
                self.hotkey_var.set(hotkey_combo_name(hotkey_mods, hotkey_vk))
            else:
                self.hotkey_var.set("None")
            self.hotkey_btn.config(bg="#444")

        if _toggle_event.is_set():
            _toggle_event.clear()
            self._do_hotkey_toggle()

        if _osd_event_on.is_set():
            _osd_event_on.clear()
            self._show_osd("ON", "#27ae60")
        if _osd_event_off.is_set():
            _osd_event_off.clear()
            self._show_osd("OFF", "#c0392b")

        if _save_pending.is_set():
            _save_pending.clear()
            _do_save_config()

        self.root.after(50, self._poll_hotkey)

    def _do_hotkey_toggle(self):
        global _all_paused, _remembered_wasd, _remembered_smart
        global wasd_enabled, smart_enabled

        if not _all_paused:
            if not wasd_enabled and not smart_enabled:
                self.toggle_wasd()
                self.toggle_smart()
                _remembered_wasd  = True
                _remembered_smart = True
                _all_paused = False
                _log_queue.append("All enabled via hotkey")
                _osd_event_on.set()
                return

            _remembered_wasd  = wasd_enabled
            _remembered_smart = smart_enabled
            if wasd_enabled:
                self.toggle_wasd()
            if smart_enabled:
                self.toggle_smart()
            _all_paused = True
            _log_queue.append("Paused via hotkey")
            _osd_event_off.set()
        else:
            if _remembered_wasd and not wasd_enabled:
                self.toggle_wasd()
            if _remembered_smart and not smart_enabled:
                self.toggle_smart()
            _all_paused = False
            _log_queue.append("Resumed via hotkey")
            _osd_event_on.set()

    def _show_osd(self, text, color):
        if self._osd_window:
            try:
                self._osd_window.destroy()
            except Exception:
                pass
            self._osd_window = None

        osd = tk.Toplevel(self.root)
        osd.overrideredirect(True)
        osd.attributes("-topmost", True)
        osd.attributes("-alpha", 0.85)
        osd.configure(bg="#111")

        frame = tk.Frame(osd, bg="#111", padx=8, pady=2)
        frame.pack()

        tk.Label(
            frame, text=f"WT: {text}",
            fg=color, bg="#111", font=("Segoe UI", 9, "bold")
        ).pack()

        osd.update_idletasks()
        ow = osd.winfo_width()
        oh = osd.winfo_height()

        tibia_rect = get_tibia_rect()
        if tibia_rect:
            tx, ty, tw, th = tibia_rect
            x = tx + (tw - ow) // 2
            y = ty + 8
        else:
            sw = osd.winfo_screenwidth()
            sh = osd.winfo_screenheight()
            x = (sw - ow) // 2
            y = (sh - oh) // 3

        osd.geometry(f"+{x}+{y}")

        self._osd_window = osd
        osd.after(1500, self._close_osd)

    def _close_osd(self):
        if self._osd_window:
            try:
                self._osd_window.destroy()
            except Exception:
                pass
            self._osd_window = None

    def toggle_wasd(self):
        global wasd_enabled
        if wasd_enabled:
            wasd_enabled = False
            wasd_held.clear()
            self.wasd_var.set("OFF")
            self.wasd_btn.config(bg=self.RED)
            _log_queue.append("WASD: disabled")
        else:
            wasd_enabled = True
            self.wasd_var.set("ON")
            self.wasd_btn.config(bg=self.GREEN)
            _log_queue.append("WASD: enabled")

    def toggle_smart(self):
        global smart_enabled
        if smart_enabled:
            smart_enabled = False
            arrow_held.clear()
            self.smart_var.set("OFF")
            self.smart_btn.config(bg=self.RED)
            _log_queue.append("Smart: disabled")
        else:
            smart_enabled = True
            self.smart_var.set("ON")
            self.smart_btn.config(bg=self.GREEN)
            _log_queue.append("Smart: enabled")

    def _poll_log(self):
        while _log_queue:
            msg = _log_queue.pop(0)
            self.log_text.config(state="normal")
            self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(200, self._poll_log)

    def _real_close(self):
        global wasd_enabled, smart_enabled
        wasd_enabled = False
        smart_enabled = False
        self.output.stop()
        try:
            handle = getattr(_install_hook, '_handle', None)
            if handle:
                user32.UnhookWindowsHookEx(handle)
        except Exception:
            pass
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.root.destroy()
        os._exit(0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False

    if not is_admin:
        _log_queue.append("NOT running as Admin!")
        _log_queue.append("  Right-click > Run as administrator")

    app = App()
    app.run()
