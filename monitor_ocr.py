import platform
import threading
import time
import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab
import pytesseract
import pyautogui
import re

# === CONFIGURAÇÃO DO TESSERACT ===
# Ajuste o caminho se o tesseract não estiver no PATH do sistema:
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except AttributeError:
    pass  # caso já esteja configurado no PATH

# === CALIBRAÇÃO INTERATIVA DO BBOX ===
print("Calibração: posicione o mouse no canto superior-esquerdo do número e pressione Enter")
input()
x1, y1 = pyautogui.position()
print(f"Superior-Esquerdo: ({x1}, {y1})")
print("Agora posicione o mouse no canto inferior-direito do número e pressione Enter")
input()
x2, y2 = pyautogui.position()
print(f"Inferior-Direito: ({x2}, {y2})")

# Validação da região calibrada
dx = x2 - x1
dy = y2 - y1
if dx <= 0 or dy <= 0:
    print(f"Erro: região inválida (w={dx}, h={dy}).")
    exit(1)

# Margem extra (10% ou mínimo 5px)
pad_x = max(5, dx // 10)
pad_y = max(5, dy // 10)
x1p = max(0, x1 - pad_x)
y1p = max(0, y1 - pad_y)
x2p = x2 + pad_x
y2p = y2 + pad_y

# Define BBOX calibrado com margem
BBOX = (x1p, y1p, x2p, y2p)
print(f"Usando BBOX calibrado (com margem): {BBOX} (w={x2p-x1p}, h={y2p-y1p})")

# === PARÂMETROS DE MONITORAMENTO ===
THRESHOLD = 16.60  # valor para disparar alerta
INTERVAL = 2       # intervalo em segundos entre capturas

# === ALERTA SONORO (Windows) ===
if platform.system() == "Windows":
    import winsound
    SOUND_AVAILABLE = True
else:
    SOUND_AVAILABLE = False

# === FUNÇÕES PRINCIPAIS ===

def capture_and_ocr():
    """Captura a região definida por BBOX e retorna texto OCR."""
    img = ImageGrab.grab(bbox=BBOX)
    img.save("debug.png")  # debug
    gray = img.convert("L")  # tons de cinza
    config = r'-c tessedit_char_whitelist=0123456789., --psm 6'
    return pytesseract.image_to_string(gray, config=config, lang="eng+por").strip()


def parse_price(text):
    """Extrai float válido de OCR com validação de formato."""
    t = text.strip()
    # Apenas form. 0.00 ou 0,00 até 4 dígitos antes
    if not re.match(r'^[0-9]{1,4}[.,][0-9]{2}$', t):
        return None
    t = t.replace(',', '.')
    try:
        v = float(t)
    except ValueError:
        return None
    # limite realista
    if v < 0.01 or v > 1000:
        return None
    return v


def check_ocr_loop():
    """Loop de captura, parse e atualização da GUI."""
    while True:
        raw = capture_and_ocr()
        value = parse_price(raw)
        print(f"Raw OCR: '{raw}' -> Parsed: {value}")
        root.after(0, lambda r=raw: raw_var.set(r if r else '(vazio)'))
        if value is not None:
            formatted = f"{value:.2f}".replace('.', ',')
            root.after(0, lambda f=formatted: price_var.set(f))
            if value >= THRESHOLD and not alerted[0]:
                alerted[0] = True
                root.after(0, lambda: alert(value))
        else:
            root.after(0, lambda r=raw: price_var.set(f"?{r}"))
        time.sleep(INTERVAL)


def alert(value):
    """Exibe alerta visual e sonoro."""
    messagebox.showwarning("🔔 ALERTA OCR",
                           f"Preço por OCR: {value:.2f} ≥ {THRESHOLD:.2f}")
    if SOUND_AVAILABLE:
        winsound.PlaySound("resources/alert.wav",
                           winsound.SND_FILENAME | winsound.SND_ASYNC)

# === GUI ===
root = tk.Tk()
root.title("Monitor OCR de Cotação")

# Texto cru OCR
tk.Label(root, text="Raw OCR:", font=("Arial", 10)).pack()
raw_var = tk.StringVar(master=root, value="—")
tk.Label(root, textvariable=raw_var, font=("Arial", 12)).pack(pady=2)

# Preço formatado
tk.Label(root, text="Preço Reconhecido:", font=("Arial", 14)).pack()
price_var = tk.StringVar(master=root, value="—")
tk.Label(root, textvariable=price_var, font=("Arial", 36, "bold")).pack(pady=5)

# Threshold
tk.Label(root, text=f"Alerta ≥ {THRESHOLD:.2f}".replace('.', ','), font=("Arial", 10)).pack(pady=2)

alerted = [False]
threading.Thread(target=check_ocr_loop, daemon=True).start()
root.mainloop()

