from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

def enviar_whatsapp(numero, mensagem):
    print("Abrindo o navegador Chrome...")
    # Inicializa o Chrome com o ChromeDriver correto
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(f'https://web.whatsapp.com/send?phone={numero}&text={mensagem}')
    print("Aguardando o WhatsApp Web carregar (faça o login pelo QR Code se solicitado)...")
    time.sleep(20)  # Tempo para login pelo QR Code, ajuste conforme necessário

    try:
        # Tenta encontrar a caixa de mensagem (30 tentativas, até 1 min)
        for tentativas in range(30):
            try:
                # Pode ser necessário ajustar o XPath se o WhatsApp Web mudar o layout
                caixa = driver.find_element(By.XPATH, '//div[@contenteditable="true" and @data-tab="10"]')
                caixa.send_keys(Keys.ENTER)
                print("Mensagem enviada com sucesso via WhatsApp Web!")
                break
            except Exception:
                time.sleep(2)
        else:
            print("Não localizou a caixa de mensagem (WhatsApp Web pode não ter carregado corretamente).")
    except Exception as e:
        print(f"Falha ao enviar mensagem: {e}")
    finally:
        time.sleep(4)
        #driver.quit()

# ===== Exemplo de uso =====
if __name__ == "__main__":
    numero = "5562984537185"  # Substitua pelo seu número (DDI + DDD + número, ex: 5511999999999)
    mensagem = "Teste automático via Selenium WhatsApp Web"
    enviar_whatsapp(numero, mensagem)
