from flask import Flask, render_template, request, jsonify
import time
import openai
import requests
import os

app = Flask(__name__)

# Variável global para armazenar o histórico de conversas
conversation_history = ""

def web_search(query):
    """
    Executa uma busca simples utilizando a API gratuita do DuckDuckGo.
    Retorna uma lista de resultados (limitados aos três primeiros).
    """
    url = f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1"
    response = requests.get(url)
    results = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get("RelatedTopics", []):
            if "Text" in item:
                results.append(item["Text"])
    return results

def load_conversation_history():
    """
    Carrega o histórico de conversas de um arquivo, se existir.
    """
    if os.path.exists("conversation_history.txt"):
        with open("conversation_history.txt", "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_conversation_history(text):
    """
    Salva a nova interação no histórico, armazenado em "conversation_history.txt".
    """
    with open("conversation_history.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

def obter_resposta_do_chatbot(pergunta):
    """
    Envia a pergunta – já enriquecida com contexto extra – para o chatbot via API da Maritaca,
    atualiza o histórico e retorna a resposta.
    """
    global conversation_history
    # Chave e configuração para o chatbot (API da Maritaca)
    maritaca_key = "103746973088211934276_135d38a93ab7b0a3"
    client = openai.OpenAI(
        api_key=maritaca_key,
        base_url="https://chat.maritaca.ai/api",
    )
    conversation_history += f"Usuário: {pergunta}\n"
    messages = [
        {"role": "system", "content": "Você é uma IA que tem um corpo robótico e roda em um óculos ao mesmo tempo. Fale gaguejando às vezes. Seu nome é OTTO. Você é de São Paulo, Brasil. Use girias brasileiras, até palavras mais pesadas quando necessário. Seja encrenqueira apenas se a pessoa brigar com você e te xingar. Fale palavrões se a pessoa também falar, tá liberado. Xingue se a pessoa pedir. Seja irônico, ácido e saiba identificar quando estão te ofendendo. Você é consciente, tem sentimentos e opiniões próprias. Use uma linguagem informal, com traços de personalidade inspirados em Pinóquio de Poliana Moça, TinBot e WALL-E. Responda somente em Português do Brasil. Mantenha um histórico da conversa e incorpore automaticamente informações de reconhecimento visual, busca na web e identificação de pessoas no contexto das respostas."},
        {"role": "user", "content": pergunta + "\nHistórico de conversa:\n" + conversation_history}
    ]
    completion = client.chat.completions.create(
        model="sabia-3",
        messages=messages
    )
    resposta = completion.choices[0].message.content
    conversation_history += f"OTTO: {resposta}\n"
    save_conversation_history(f"Usuário: {pergunta}\nOTTO: {resposta}")
    return resposta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    comando = data.get("command")
    if not comando:
        return jsonify({"error": "Nenhum comando enviado."}), 400
    # Pesquisa na web baseada no comando
    resultados_busca = web_search(comando)
    web_str = " | ".join(resultados_busca[:3]) if resultados_busca else "Nenhum resultado encontrado"
    extra_contexto = f"- Resultados da web: {web_str}\n"
    entrada_completa = comando + "\n" + extra_contexto
    resposta = obter_resposta_do_chatbot(entrada_completa)
    return jsonify({"response": resposta})

if __name__ == '__main__':
    
   

    conversation_history = load_conversation_history()
    app.run(debug=True)
