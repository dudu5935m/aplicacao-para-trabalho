from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.short_keys = False
# Lista de peças

estoque_pecas = [
    {
        "id": 1,
        "tipo_peca": "Bracinho do ajuste",
        "para_que_serve": "Para ajustar o transfer na base",
        "cod_produto": "BR-001",
        "quantidade": 20
    },
    {
        "id": 2,
        "tipo_peca": "bracinho de tranporte",
        "para_que_serve": "Para transportar o transfer até a base",
        "cod_produto": "BR-002",
        "quantidade": 5
    },
    {
        "id": 3,
        "tipo_peca": "O 'U' para o transporte",
        "para_que_serve": "Ele serve para trocar o sistema antigo de transporte, e melhora o funcionamento da maquina",
        "cod_produto": "U-003",
        "quantidade": 10
    }
]

@app.route('/')
def home():
    return "Hello World!"

@app.route('/pecas', methods=['GET'])
def get_pecas():
    return jsonify({"Menssagem" : "Lista de peças","Dados" : estoque_pecas})

@app.route('/lista_pecas', methods=['GET'])
def lista_pecas():
    pecas_filtradas = [pecas for pecas in estoque_pecas if pecas['quantidade'] >= 10 ]  
    return jsonify({"Menssagem" : "Lista de peças com quantidade maior que 10","Dados" : pecas_filtradas})

@app.route('/pecas/para_que_serve', methods=['GET'])
def Lista_pecas_para_que_serve():
    pecas_para_que_serve = [pecas['para_que_serve'] for pecas in estoque_pecas]
    return jsonify({"Menssagem" : "Lista de peças e para que serve","Dados" : pecas_para_que_serve})

@app.route('/pecas/quantidade_cod', methods=['GET'])
def Lista_pecas_id_quantidade_cod():
    pecas_id_quantidade_cod = [{ "cod_produto": peca['cod_produto'], "quantidade": peca['quantidade'], } for peca in estoque_pecas]
    return jsonify({"Menssagem" : "Lista de peças com id, quantidade e código do produto","Dados" : pecas_id_quantidade_cod})

@app.route('/pecas_vendidas', methods=['POST'])
def pecas_vendidas():
    pecas_vendidas = request.json
    request_cod_produto = pecas_vendidas['cod_produto']
    request_quantidade = pecas_vendidas['quantidade']
    valid_cod_pecas = next((pecas for pecas in estoque_pecas if pecas['cod_produto'] == request_cod_produto), None)

    if not valid_cod_pecas:
        return jsonify({"Menssagem": "Código do produto inválido"}), 400
    
    else :
        return jsonify({"Menssagem": "Código do produto válido"}), 201


    
    

app.run()