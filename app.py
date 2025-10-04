from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    msg = request.form.get("Body").strip().lower()
    resp = MessagingResponse()
    reply = resp.message()

    if "treino" in msg:
        reply.body("hoje é dia de peito e tríceps! Bora malhar!")
    elif "oi" in msg or "eai" in msg:
        reply.body("Eai, tudo bem? Quer saber qual treino fazer hoje?")
    else:
        reply.body("Desculpa, não entendi. Responda com 'treino' para saber o treino do dia.")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000) 