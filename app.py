from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json

app = Flask(__name__)

TREINOS_FILE = "treinos.json"

# ============================
# funções auxiliares
# ============================
def carregar_treinos():
    if not os.path.exists(TREINOS_FILE):
        with open(TREINOS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
    with open(TREINOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_treinos(data):
    with open(TREINOS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ============================
# funções principais
# ============================
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    msg = request.form.get("Body").strip().lower()
    resp = MessagingResponse()
    reply = resp.message()
    treinos = carregar_treinos()

    parts = msg.split()
    comando = parts[0] if parts else ""

    if comando == "adicionar" and len(parts) >= 3:
        dia = parts[1]
        treino = " ".join(parts[2:])
        treinos.setdefault(dia, []).append(treino)
        salvar_treinos(treinos)
        reply.body(f"Adicionado '{treino}' ao treino de {dia.capitalize()}.")

    elif comando == "remover" and len(parts) >= 3:
        dia = parts[1]
        treino = " ".join(parts[2:])
        if dia in treinos and treino in treinos[dia]:
            treinos[dia].remove(treino)
            salvar_treinos(treinos)
            reply.body(f"Removido '{treino}' do treino de {dia.capitalize()}.")
        else:
            reply.body(f"Não encontrei '{treino}' em {dia.capitalize()}.")

    elif comando == "treino" and len(parts) == 2:
        dia = parts[1]
        if dia in treinos and treinos[dia]:
            lista = "\n- ".join(treinos[dia])
            reply.body(f"Treino de {dia.capitalize()}:\n- {lista}")
        else:
            reply.body(f"Não há treino registrado para {dia.capitalize()}.")

    elif comando == "listar":
        if treinos:
            resposta = "Treinos registrados:\n"
            for dia, exercicios in treinos.items():
                lista = "\n- ".join(exercicios)
                resposta += f"{dia.capitalize()}:\n- {lista}\n"
            reply.body(resposta)
        else:
            reply.body("Nenhum treino registrado.")
    else:
        reply.body(
            "Comandos disponíveis:\n"
            "- treino [dia]\n"
            "- adicionar [dia] [exercicio]\n"
            "- remover [dia] [exercicio]\n"
            "- listar"
        )

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)

