#! /bin/env python3

from flask import Flask, request, make_response
from flask_cors import CORS
from loguru import logger
import logging
import datetime
import json

class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())

app = Flask(__name__)
CORS(app) 
app.logger.addHandler(InterceptHandler())

class Message:
    def __init__(self, id: int, sender: str, text: str):
        self.id = id
        self.when = datetime.datetime.now().isoformat()
        self.sender = sender
        self.text = text

    def ToStr(self):
        return f'[{self.id:06}] {self.when} {self.sender} -> {self.text}'

    def ToJson(self):
        return {
            'id': self.id,
            'when': self.when,
            'sender': self.sender,
            'text': self.text
        }

messages = []
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
}

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat</title>
    <script>
        let lastMessageId = 0; // ID da última mensagem recebida

        async function fetchMessages() {            
            let url = `http://192.168.1.9:8080/message/${lastMessageId}`;            

            console.log('Buscando mensagens:', url);

            resp = await fetch(url, {
                method: 'GET',                
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log(resp);

            txt = await resp.text();

            console.log(txt);

            data = await JSON.parse(txt);

            const messages = data.messages;

            if (messages.length > 0) {
                updateTable(messages);
                lastMessageId = messages[messages.length-1].id + 1;
                console.log('Última mensagem:', lastMessageId);
            }            
        }

        function updateTable(data) {
            const tableBody = document.getElementById('messagesTableBody');

            data.forEach(item => {
                const row = document.createElement('tr');

                const whenCell = document.createElement('td');
                whenCell.textContent = item.when;
                row.appendChild(whenCell);

                const idCell = document.createElement('td');
                idCell.textContent = item.id;
                row.appendChild(idCell);

                const senderCell = document.createElement('td');
                senderCell.textContent = item.sender;
                row.appendChild(senderCell);

                const textCell = document.createElement('td');
                textCell.textContent = item.text;
                row.appendChild(textCell);

                tableBody.appendChild(row);
            });
        }

        function sendMessage(event) {
            event.preventDefault(); // Impede o envio padrão do formulário
            
            const formData = new FormData();
            const sender = document.getElementById('sender').value;
            const text = document.getElementById('text').value;
            
            formData.append("sender", sender);
            formData.append("text", text);

            console.log('Enviando mensagem:', sender, text);

            fetch('http://192.168.1.9:8080/message', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log('Sucesso:', data);
                document.getElementById('messageForm').reset(); // Reseta o formulário após o envio
                fetchMessages(); // Atualiza a tabela imediatamente após enviar a mensagem
            })
            .catch(error => console.error('Erro:', error));
        }

        // Iniciar o request GET a cada 5 segundos
        setInterval(fetchMessages, 5000);

        // Fazer o primeiro request imediatamente após a página carregar
        window.onload = fetchMessages;
    </script>
</head>
<body>
    <h1>Chat</h1>

    <!-- Formulário para enviar mensagens -->
    <form id="messageForm" onsubmit="sendMessage(event)">
        <label for="sender">Nome:</label>
        <input type="text" id="sender" name="sender" required>
        
        <label for="text">Mensagem:</label>
        <input type="text" id="text" name="text" required>
        
        <button type="submit">Enviar</button>
    </form>

    <!-- Tabela para exibir as mensagens -->
    <h2>Mensagens:</h2>
    <table border="1">
        <thead>
            <tr>
                <th>Data</th>
                <th>ID</th>
                <th>Nome</th>
                <th>Mensagem</th>
            </tr>
        </thead>
        <tbody id="messagesTableBody">
            <!-- Linhas da tabela serão adicionadas aqui dinamicamente -->
        </tbody>
    </table>
</body>
</html>

"""

def resp(body: dict, status_code):
    body['timestamp'] = datetime.datetime.now().isoformat()
    ret = make_response(json.dumps(body))
    ret.headers = headers
    ret.status_code = status_code
    return ret

@app.route('/message', methods=['POST'])
def post_message():
    try:
        sender = request.form.get('sender')
        text = request.form.get('text')

        if sender is None or len(sender) == 0:
            logger.error("Sender is empty")
            return resp({
                "error": "Empty sender",
            }, 400)
            

        if text is None or len(text) == 0:
            logger.error("Text is empty")
            return resp({
                "error": "Empty text"                
            }, 400)

        message = Message(len(messages), sender, text)
        messages.append(message)

        logger.info(f'Received message: {message.ToStr()}')

        return resp({
            "id": message.id
            }, 201)
    except Exception as e:
        logger.error(f'Error processing message: {e}')
        return resp({
            "error": str(e)
            }, 500)

@app.route('/message/<last>', methods=['GET'])
def get_messages(last: int = 0):
    try:
        ret = []
        if not last.isdigit():
            return resp({
                "error": "Invalid message index"
            }, 400)
        
        last = int(last)
        if last < 0:
            last = 0

        if last >= len(messages):
            return resp({
                "messages": ret
                }, 200)

        for m in messages[last:]:
            ret.append(m.ToJson())

        logger.info(f"Returning {len(ret)} messages messages from {last}: {ret}")
        return resp({
            "messages": ret
            }, 200)
    except Exception as e:
        logger.error(f'Error processing message: {e}')
        return resp({
            "error": str(e)
            }, 500)

def start_app():
    logger.info('Starting Chat Doenca API')
    from waitress import serve
    serve(app, host='192.168.1.9' port=8080)
    logger.info('Exiting Chat Doenca API')