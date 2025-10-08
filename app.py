from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json
from flask import Response

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

# normaliza o dia para ter a primeira letra maiúscula e o resto minúsculo
def normalizar_dia(dia):
    return dia.lower().capitalize()

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

    user = request.form.get("From")  # ex: 'whatsapp:+5511999999999'
    treinos.setdefault(user, {})

    if comando == "add" and len(parts) >= 3:
        dia = normalizar_dia(parts[1])
        treino = " ".join(parts[2:])
        treinos.setdefault(user, {}).setdefault(dia, [])

        if treino not in treinos[user][dia]:
            treinos[user][dia].append(treino)
            salvar_treinos(treinos)
            reply.body(f"✅ Adicionado '{treino}' ao treino de {dia}.")
        else:
            reply.body(f"⚠️ '{treino}' já está no treino de {dia}.")

    elif comando == "remover" and len(parts) >= 3:
        dia = normalizar_dia(parts[1])
        treino = " ".join(parts[2:])
        if dia in treinos[user] and treino in treinos[user][dia]:
            treinos[user][dia].remove(treino)
            salvar_treinos(treinos)
            reply.body(f"❌ Removido '{treino}' do treino de {dia}.")
        else:
            reply.body(f"❌ Não encontrei '{treino}' em {dia}.")

    elif comando == "clear" and len(parts) == 2:
        dia = normalizar_dia(parts[1])
        if dia in treinos:
            treinos[dia] = []
            salvar_treinos(treinos)
            reply.body(f"🧹 Todos os treinos de {dia.capitalize()} foram removidos.")
        else:
            reply.body(f"❌ Não há treinos para {dia.capitalize()}.")

    elif comando == "treino" and len(parts) == 2:
        dia = normalizar_dia(parts[1])
        if dia in treinos and treinos[dia]:
            lista = "\n- ".join(treinos[dia])
            reply.body(f"💪 Treino de {dia.capitalize()}:\n- {lista}")
        else:
            reply.body(f"❌ Não há treino registrado para {dia.capitalize()}.")

    elif comando == "ls":
        if treinos:
            resposta = "🏋️ Treinos registrados:\n"
            for dia, exercicios in treinos.items():
                lista = "\n- ".join(exercicios)
                resposta += f"{dia.capitalize()}:\n- {lista}\n"
            reply.body(resposta)
        else:
            reply.body("❌ Nenhum treino registrado.")

    elif comando == "help":
        reply.body(
            "🔥 Comandos disponíveis 🔥:\n"
            "- 💪 treino [dia]\n"
            "- ✅ add [dia] [exercicio]\n"
            "- ❌ remover [dia] [exercicio]\n"
            "- 🧹 clear [dia] (remove todos)\n"
            "- 🗒️ ls"
    )
        
    else:
        reply.body("❓ Comando inválido. Envie 'help' para ver os comandos disponíveis.")

    return Response(str(resp), mimetype="application/xml")

if __name__ == "__main__":
    app.run(port=5000)

