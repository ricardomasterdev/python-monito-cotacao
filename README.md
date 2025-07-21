# 📈 Monitor OCR de Cotações com Alerta WhatsApp

Projeto em Python para monitorar cotações exibidas na tela do seu computador, utilizando OCR para captura automática do preço, com envio de **alerta via WhatsApp** (usando seu número e WhatsApp Web) assim que um valor-alvo é atingido.

---

## ✨ Funcionalidades

- 🎯 **Reconhecimento automático** de preço em qualquer área da tela via OCR calibrado
- 🚨 **Alerta automático** no WhatsApp quando o valor for atingido
- 💬 Integração com WhatsApp Web via Selenium (login QR Code, sem API externa)
- 🖼️ Interface gráfica simples para acompanhamento em tempo real (Tkinter)
- ⏹️ Encerramento automático após ciclos pós-alerta, com mensagem final
- 🪟 Suporte completo para Windows

---

## ⚙️ Instalação e Configuração

### 1. Clone o repositório

```sh
git clone https://github.com/ricardomasterdev/python-monito-cotacao.git
cd seurepo
2. Crie um ambiente virtual Python (recomendado)
sh
Copiar
Editar
python -m venv .venv
.venv\Scripts\activate
3. Instale as dependências
sh
Copiar
Editar
pip install -r requirements.txt
<details> <summary><strong>Exemplo de <code>requirements.txt</code></strong></summary>
text
Copiar
Editar
pillow
pytesseract
pyautogui
selenium
webdriver-manager
tk
</details>
4. Instale o Tesseract OCR
Baixe e instale o Tesseract OCR para Windows

Após instalar, adicione ao PATH ou ajuste no seu script:

python
Copiar
Editar
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
5. Instale o Google Chrome
O Selenium/WebDriver utiliza o Chrome para acessar o WhatsApp Web.

Baixe o Google Chrome se ainda não estiver instalado.

▶️ Como Usar
Execute o script principal do projeto:

sh
Copiar
Editar
python monitor_ocr_whatsapp.py
Calibre a área de captura
Siga as instruções do console para posicionar o mouse nos cantos da região onde o preço aparece na tela (confirma com ENTER).

Login no WhatsApp Web
O Chrome abrirá automaticamente. Faça login com o QR Code exibido na primeira execução.
(A sessão ficará salva para os próximos usos.)

Monitoramento automático
O programa reconhece a cotação em tempo real.
Assim que atingir o valor-alvo, envia uma mensagem automática no seu WhatsApp e, após 4 ciclos extras, envia mensagem de encerramento e fecha o sistema.

🛠️ Configuração do Monitoramento
Altere facilmente no código:

Parâmetro	O que faz	Onde ajustar	Exemplo
THRESHOLD	Valor do alerta	topo do script	THRESHOLD = 3.46
INTERVAL	Intervalo entre capturas	topo do script	INTERVAL = 2
numero	Seu número WhatsApp	no script (com DDI e DDD)	5511999999999
mensagem	Texto do alerta	no script	"Alerta: cotação atingida!"

💡 Dicas & Solução de Problemas
QR Code do WhatsApp não aparece: Traga o Chrome para frente, aguarde carregamento completo.

Erro do Selenium/WebDriver: Instale webdriver-manager e mantenha o Chrome atualizado.

Tesseract não encontrado: Ajuste o caminho em pytesseract.pytesseract.tesseract_cmd.

Permissões: Execute o terminal como administrador se necessário.

XPath da caixa de mensagem não encontrado: Atualize o Selenium e veja se o WhatsApp Web mudou o layout (mande o erro aqui se precisar de ajuda!).

📋 Requisitos
Windows 10 ou 11

Python 3.9 ou superior

Tesseract OCR instalado e configurado

Google Chrome instalado

Permissão para abrir janelas e automação

🙌 Créditos e Recursos
Tesseract OCR

PyAutoGUI

Pillow

Selenium Python

Webdriver Manager

Tkinter

