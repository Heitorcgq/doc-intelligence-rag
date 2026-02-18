from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from cerebro import perguntar_ao_bot

app = Flask(__name__)

@app.route("/bot", methods=['POST'])
def bot():
    # 1. Recebe a mensagem do WhatsApp
    msg_usuario = request.values.get('Body', '').strip()
    
    print(f"📩 Mensagem recebida: {msg_usuario}")

    # 2. Pergunta ao Cérebro (que consulta o PDF)
    resposta_ia = perguntar_ao_bot(msg_usuario)
    
    print(f"🤖 Resposta da IA: {resposta_ia}")

    # 3. Devolve para o WhatsApp
    resp = MessagingResponse()
    resp.message(resposta_ia)

    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)