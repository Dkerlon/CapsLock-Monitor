"""
CapsLock Monitor com timer de silêncio configurável.
Dependências: pip install pynput pystray pillow
Execução:     python capslock_monitor.pyw
"""

import threading
import time
import tkinter as tk
from tkinter import ttk
from pynput import keyboard

_caps_active   = False
_lock          = threading.Lock()

_silent_until  = 0.0
_silent_lock   = threading.Lock()

def show_popup(is_caps_on: bool) -> None:
    with _silent_lock:
        if time.time() < _silent_until:
            return

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.0)

    if is_caps_on:
        bg, accent, dot_color, label = "#E8F5E3", "#2E7D32", "#4CAF50", "CAPS  ON"
    else:
        bg, accent, dot_color, label = "#F5F5F5", "#424242", "#BDBDBD", "CAPS  OFF"

    root.configure(bg=bg)
    border = tk.Frame(root, bg=accent, padx=1, pady=1)
    border.pack(fill="both", expand=True)
    inner  = tk.Frame(border, bg=bg, padx=14, pady=9)
    inner.pack(fill="both", expand=True)
    row    = tk.Frame(inner, bg=bg)
    row.pack()

    cv = tk.Canvas(row, width=8, height=8, bg=bg, highlightthickness=0)
    cv.create_oval(1, 1, 7, 7, fill=dot_color, outline="")
    cv.pack(side="left", padx=(0, 7), pady=3)

    tk.Label(row, text=" ".join(label),
             font=("Courier New", 11, "bold"),
             bg=bg, fg=accent).pack(side="left")

    root.update_idletasks()
    w  = inner.winfo_reqwidth()  + 30
    h  = inner.winfo_reqheight() + 20
    sw = root.winfo_screenwidth()
    root.geometry(f"{w}x{h}+{sw - w - 16}+16")

    steps, delay = 10, 18

    def fade_in(s=0):
        if s <= steps:
            root.attributes("-alpha", s / steps * 0.95)
            root.after(delay, fade_in, s + 1)
        else:
            root.after(800, fade_out)

    def fade_out(s=0):
        if s <= steps:
            root.attributes("-alpha", (steps - s) / steps * 0.95)
            root.after(delay, fade_out, s + 1)
        else:
            root.destroy()

    root.after(10, fade_in)
    root.mainloop()


def open_settings() -> None:
    win = tk.Tk()
    win.title("CapsAlert — Configurações")
    win.resizable(False, False)
    win.attributes("-topmost", True)

    BG, FG, ACC = "#F5F5F5", "#212121", "#2E7D32"
    win.configure(bg=BG)

    hdr = tk.Frame(win, bg=ACC, padx=20, pady=12)
    hdr.pack(fill="x")
    tk.Label(hdr, text="C A P S A L E R T",
             font=("Courier New", 13, "bold"),
             bg=ACC, fg="white").pack(side="left")

    body = tk.Frame(win, bg=BG, padx=20, pady=18)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Timer de silêncio",
             font=("Courier New", 10, "bold"),
             bg=BG, fg=FG).grid(row=0, column=0, columnspan=3,
                                sticky="w", pady=(0, 6))

    tk.Label(body, text="Duração (min):",
             font=("Courier New", 9),
             bg=BG, fg="#616161").grid(row=1, column=0, sticky="w")

    duration_var = tk.IntVar(value=5)
    spin = tk.Spinbox(body, from_=1, to=120, textvariable=duration_var,
                      width=5, font=("Courier New", 10),
                      bg="white", fg=FG, relief="flat",
                      highlightthickness=1, highlightbackground="#BDBDBD",
                      buttonbackground="#E0E0E0")
    spin.grid(row=1, column=1, padx=(8, 4), sticky="w")

    tk.Label(body, text="minutos", font=("Courier New", 9),
             bg=BG, fg="#9E9E9E").grid(row=1, column=2, sticky="w")

    status_var = tk.StringVar(value="Inativo")
    status_lbl = tk.Label(body, textvariable=status_var,
                          font=("Courier New", 8),
                          bg=BG, fg="#9E9E9E")
    status_lbl.grid(row=2, column=0, columnspan=3, sticky="w", pady=(4, 12))

    def _tick():
        with _silent_lock:
            remaining = _silent_until - time.time()
        if remaining > 0:
            m, s = divmod(int(remaining), 60)
            status_var.set(f"Silencioso por mais {m:02d}:{s:02d}")
            win.after(1000, _tick)
        else:
            status_var.set("Inativo")

    def start_timer():
        global _silent_until
        mins = duration_var.get()
        with _silent_lock:
            _silent_until = time.time() + mins * 60
        status_var.set("Iniciando…")
        win.after(200, _tick)

    def stop_timer():
        global _silent_until
        with _silent_lock:
            _silent_until = 0.0
        status_var.set("Inativo")

    btn_frame = tk.Frame(body, bg=BG)
    btn_frame.grid(row=3, column=0, columnspan=3, sticky="ew")

    btn_cfg = dict(font=("Courier New", 9, "bold"), relief="flat",
                   padx=14, pady=6, cursor="hand2")

    tk.Button(btn_frame, text="▶  Iniciar", bg=ACC, fg="white",
              activebackground="#1B5E20", activeforeground="white",
              command=start_timer, **btn_cfg).pack(side="left", padx=(0, 8))

    tk.Button(btn_frame, text="■  Parar", bg="#E0E0E0", fg=FG,
              activebackground="#BDBDBD", activeforeground=FG,
              command=stop_timer, **btn_cfg).pack(side="left")

    tk.Frame(body, bg="#E0E0E0", height=1).grid(
        row=4, column=0, columnspan=3, sticky="ew", pady=(16, 10))

    tk.Button(body, text="Fechar", bg=BG, fg="#9E9E9E",
              activebackground="#EEEEEE", relief="flat",
              font=("Courier New", 8), cursor="hand2",
              command=win.destroy).grid(row=5, column=0, columnspan=3)

    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    ww, wh = win.winfo_reqwidth(), win.winfo_reqheight()
    win.geometry(f"{ww}x{wh}+{(sw-ww)//2}+{(sh-wh)//2}")

    with _silent_lock:
        if _silent_until > time.time():
            win.after(200, _tick)

    win.mainloop()


def start_tray() -> None:
    try:
        import pystray
        from PIL import Image, ImageDraw

        def make_icon(on: bool):
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            d   = ImageDraw.Draw(img)
            color = "#4CAF50" if on else "#9E9E9E"
            d.ellipse([8, 8, 56, 56], fill=color)
            d.rectangle([28, 18, 36, 38], fill="white")
            d.rectangle([28, 42, 36, 48], fill="white")
            return img

        icon = pystray.Icon(
            "CapsAlert",
            make_icon(_caps_active),
            "CapsAlert",
            menu=pystray.Menu(
                pystray.MenuItem("Configurações", lambda: threading.Thread(
                    target=open_settings, daemon=True).start()),
                pystray.MenuItem("Sair", lambda: icon.stop()),
            )
        )
        icon.run()
    except ImportError:
        open_settings()


def detect_initial_caps() -> bool:
    try:
        import ctypes
        return bool(ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 0x0001)
    except Exception: pass
    try:
        import subprocess
        out = subprocess.check_output(["xset", "q"], stderr=subprocess.DEVNULL).decode()
        return "Caps Lock:   on" in out
    except Exception: pass
    try:
        import subprocess, re
        out = subprocess.check_output(["ioreg", "-c", "IOHIDSystem"],
                                      stderr=subprocess.DEVNULL).decode()
        m = re.search(r'"ModifierLockEnabled"\s*=\s*(\w+)', out)
        if m: return m.group(1).lower() == "yes"
    except Exception: pass
    return False


def on_key_release(key):
    global _caps_active
    if key != keyboard.Key.caps_lock:
        return
    with _lock:
        _caps_active = not _caps_active
        state = _caps_active
    threading.Thread(target=show_popup, args=(state,), daemon=True).start()


def main():
    global _caps_active
    _caps_active = detect_initial_caps()

    def run_listener():
        with keyboard.Listener(on_release=on_key_release) as listener:
            listener.join()

    threading.Thread(target=run_listener, daemon=True).start()
    
    start_tray()


if __name__ == "__main__":
    main()