#!/usr/bin/env python3
"""
CapsLock Monitor — popup minimalista no canto superior direito.
Dependência: pip install pynput
Execução:    python capslock_monitor.py   (ou .pyw para rodar sem terminal)
"""

import threading
import tkinter as tk
from pynput import keyboard

_caps_active = False
_lock = threading.Lock()


def show_popup(is_caps_on: bool) -> None:
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.0)       # começa invisível para o fade-in

    # ── Paleta ────────────────────────────────────────────────────────────
    if is_caps_on:
        bg        = "#E8F5E3"            # verde muito suave
        accent    = "#2E7D32"            # verde escuro
        dot_color = "#4CAF50"            # bolinha verde viva
        label     = "CAPS  ON"
    else:
        bg        = "#F5F5F5"            # cinza quase branco
        accent    = "#424242"            # cinza escuro
        dot_color = "#BDBDBD"            # bolinha cinza
        label     = "CAPS  OFF"

    # ── Layout compacto ───────────────────────────────────────────────────
    root.configure(bg=bg)

    # borda sutil via frame externo
    border = tk.Frame(root, bg=accent, padx=1, pady=1)
    border.pack(fill="both", expand=True)

    inner = tk.Frame(border, bg=bg, padx=14, pady=9)
    inner.pack(fill="both", expand=True)

    row = tk.Frame(inner, bg=bg)
    row.pack()

    # bolinha indicadora
    canvas = tk.Canvas(row, width=8, height=8, bg=bg,
                       highlightthickness=0)
    canvas.create_oval(1, 1, 7, 7, fill=dot_color, outline="")
    canvas.pack(side="left", padx=(0, 7), pady=3)

    # texto
    tk.Label(row, text=" ".join(label),
             font=("Courier New", 11, "bold"),
             bg=bg, fg=accent).pack(side="left")

    # ── Posição: canto superior direito ───────────────────────────────────
    root.update_idletasks()
    w = inner.winfo_reqwidth()  + 30
    h = inner.winfo_reqheight() + 20
    sw = root.winfo_screenwidth()
    margin = 16
    root.geometry(f"{w}x{h}+{sw - w - margin}+{margin}")

    # ── Animação fade-in → espera → fade-out ──────────────────────────────
    steps   = 10
    delay   = 18   # ms por step

    def fade_in(step=0):
        if step <= steps:
            root.attributes("-alpha", step / steps * 0.95)
            root.after(delay, fade_in, step + 1)
        else:
            root.after(800, fade_out)

    def fade_out(step=0):
        if step <= steps:
            root.attributes("-alpha", (steps - step) / steps * 0.95)
            root.after(delay, fade_out, step + 1)
        else:
            root.destroy()

    root.after(10, fade_in)
    root.mainloop()


# ── Detecção do estado inicial ────────────────────────────────────────────
def detect_initial_caps() -> bool:
    try:
        import ctypes
        return bool(ctypes.WinDLL("User32.dll").GetKeyState(0x14) & 0x0001)
    except Exception:
        pass
    try:
        import subprocess
        out = subprocess.check_output(["xset", "q"], stderr=subprocess.DEVNULL).decode()
        return "Caps Lock:   on" in out
    except Exception:
        pass
    try:
        import subprocess, re
        out = subprocess.check_output(["ioreg", "-c", "IOHIDSystem"],
                                      stderr=subprocess.DEVNULL).decode()
        m = re.search(r'"ModifierLockEnabled"\s*=\s*(\w+)', out)
        if m:
            return m.group(1).lower() == "yes"
    except Exception:
        pass
    return False


# ── Listener ──────────────────────────────────────────────────────────────
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
    print(f"CapsLock Monitor rodando. Estado inicial: {'ON' if _caps_active else 'OFF'}")
    with keyboard.Listener(on_release=on_key_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("Monitor encerrado.")


if __name__ == "__main__":
    main()