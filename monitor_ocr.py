import platform
import threading
import time
import tkinter as tk
from PIL import ImageGrab
import pytesseract
import pyautogui
import re
import requests  # para chamar sua API Node

# === CONFIGURAÇÃO DO TESSERACT ===
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except AttributeError:
    pass

# === PARÂMETROS DA SUA API NODE ===
API_URL      = 'http://localhost:3000/send'
API_TOKEN    = 'Ric@7901'
PHONE_NUMBER = '556284537185'

def send_whatsapp_alert(value):
    payload = {
        'numero': PHONE_NUMBER,
        'mensagem': f'Alerta OCR: cotação atingiu {value:.2f}'
    }
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        print('WhatsApp API:', resp.status_code, resp.text)
    except Exception as e:
        print('Erro ao enviar via API WhatsApp:', e)

# === CALIBRAÇÃO INTERATIVA DO BBOX ===
print("Calibração: posicione o mouse no canto superior-esquerdo do número e pressione Enter")
input()
x1, y1 = pyautogui.position()
print(f"Superior-Esquerdo: ({x1}, {y1})")

print("Agora posicione o mouse no canto inferior-direito do número e pressione Enter")
input()
x2, y2 = pyautogui.position()
print(f"Inferior-Direito: ({x2}, {y2})")

dx = x2 - x1
dy = y2 - y1
if dx <= 0 or dy <= 0:
    print(f"Erro: região inválida (w={dx}, h={dy}).")
    exit(1)

pad_x = max(5, dx // 10)
pad_y = max(5, dy // 10)
x1p, y1p = max(0, x1 - pad_x), max(0, y1 - pad_y)
x2p, y2p = x2 + pad_x, y2 + pad_y
BBOX = (x1p, y1p, x2p, y2p)
print(f"Usando BBOX calibrado (com margem): {BBOX} (w={x2p-x1p}, h={y2p-y1p})")

# === PARÂMETROS DE MONITORAMENTO ===
THRESHOLD     = 7.57  # valor que dispara o envio
INTERVAL      = 2     # segundos entre capturas
SEND_INTERVAL = 10    # segundos entre envios repetidos

def capture_and_ocr():
    img = ImageGrab.grab(bbox=BBOX)
    gray = img.convert("L")
    config = r'-c tessedit_char_whitelist=0123456789., --psm 6'
    return pytesseract.image_to_string(gray, config=config, lang="eng+por").strip()

def parse_price(text):
    t = text.strip()
    if not re.match(r'^[0-9]{1,4}[.,][0-9]{2}$', t):
        return None
    v = float(t.replace(',', '.'))
    return v if 0.01 <= v <= 1000 else None

def check_ocr_loop():
    last_send = 0.0
    while True:
        raw = capture_and_ocr()
        value = parse_price(raw)
        print(f"Raw OCR: '{raw}' -> Parsed: {value}")
        root.after(0, lambda r=raw: raw_var.set(r if r else '(vazio)'))
        if value is not None:
            formatted = f"{value:.2f}".replace('.', ',')
            root.after(0, lambda f=formatted: price_var.set(f))
            # Se >= THRESHOLD e já passou o SEND_INTERVAL desde último envio:
            now = time.time()
            if value >= THRESHOLD and (now - last_send) >= SEND_INTERVAL:
                last_send = now
                threading.Thread(target=send_whatsapp_alert, args=(value,), daemon=True).start()
        else:
            root.after(0, lambda r=raw: price_var.set(f"?{r}"))
        time.sleep(INTERVAL)

# === GUI ===
root = tk.Tk()
root.title("Monitor OCR de Cotação")

tk.Label(root, text="Raw OCR:", font=("Arial", 10)).pack()
raw_var = tk.StringVar(master=root, value="—")
tk.Label(root, textvariable=raw_var, font=("Arial", 12)).pack(pady=2)

tk.Label(root, text="Preço Reconhecido:", font=("Arial", 14)).pack()
price_var = tk.StringVar(master=root, value="—")
tk.Label(root, textvariable=price_var, font=("Arial", 36, "bold")).pack(pady=5)

tk.Label(root, text=f"Alerta ≥ {THRESHOLD:.2f}".replace('.', ','), font=("Arial", 10)).pack(pady=2)

threading.Thread(target=check_ocr_loop, daemon=True).start()
root.mainloop()
