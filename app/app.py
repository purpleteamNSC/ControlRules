import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Arquivos JSON para persistência de dados
EMPRESAS_FILE = 'data/empresas.json'
REGRAS_FILE = 'data/regras.json'
ASSOCIACOES_FILE = 'data/associacoes.json'

# Função para carregar dados de um arquivo JSON
def load_data(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Função para salvar dados em um arquivo JSON
def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    # Carregar os dados
    empresas = load_data(EMPRESAS_FILE)
    regras = load_data(REGRAS_FILE)
    associacoes = load_data(ASSOCIACOES_FILE)
    
    # Contar quantos itens existem em cada lista
    total_empresas = len(empresas)
    total_regras = len(regras)
    total_associacoes = len(associacoes)
    
    # Calcular o total de regras não associadas
    # Para isso, vamos percorrer todas as regras e verificar se elas estão associadas
    regras_associadas_ids = {associacao['regra_id'] for associacao in associacoes}
    total_regras_nao_associadas = len([regra for regra in regras if regra['id'] not in regras_associadas_ids])
    
    # Passar esses dados para o template
    return render_template('index.html', 
                           total_empresas=total_empresas, 
                           total_regras=total_regras, 
                           total_associacoes=total_associacoes,
                           total_regras_nao_associadas=total_regras_nao_associadas)



# Rota para listar empresas
@app.route('/empresas')
def list_empresas():
    empresas = load_data(EMPRESAS_FILE)
    return render_template('list_empresas.html', empresas=empresas)

# Rota para adicionar empresa
@app.route('/add_empresa', methods=['GET', 'POST'])
def add_empresa():
    if request.method == 'POST':
        nome = request.form['nome']
        helix = request.form['helix']
        
        # Verifica se já existe uma empresa com o mesmo nome
        empresas = load_data(EMPRESAS_FILE)
        if any(empresa['nome'] == nome for empresa in empresas):
            return render_template('add_empresa.html', error="Já existe uma empresa com esse nome.")
        
        # Cria a nova empresa
        empresa_id = len(empresas) + 1
        empresas.append({'id': empresa_id, 'nome': nome, 'helix': helix})
        save_data(EMPRESAS_FILE, empresas)
        return redirect(url_for('list_empresas'))
    
    return render_template('add_empresa.html')

# Rota para editar empresa
@app.route('/edit_empresa/<int:id>', methods=['GET', 'POST'])
def edit_empresa(id):
    empresas = load_data(EMPRESAS_FILE)
    empresa = next((e for e in empresas if e['id'] == id), None)
    if request.method == 'POST':
        empresa['nome'] = request.form['nome']
        empresa['helix'] = request.form['helix']
        save_data(EMPRESAS_FILE, empresas)
        return redirect(url_for('list_empresas'))
    return render_template('edit_empresa.html', empresa=empresa)

# Rota para deletar empresa
@app.route('/delete_empresa/<int:id>', methods=['POST'])
def delete_empresa(id):
    empresas = load_data(EMPRESAS_FILE)
    empresas = [e for e in empresas if e['id'] != id]
    save_data(EMPRESAS_FILE, empresas)
    return redirect(url_for('list_empresas'))

# Rota para listar regras
@app.route('/regras')
def list_regras():
    regras = load_data(REGRAS_FILE)
    return render_template('list_regras.html', regras=regras)

# Rota para listar regras nao associadas
@app.route('/regras_nao_associadas')
def regras_nao_associadas():
    # Carregar dados de regras e associações
    regras = load_data(REGRAS_FILE)
    associacoes = load_data(ASSOCIACOES_FILE)
    
    # Criar um conjunto de ids de regras associadas
    regras_associadas_ids = {associacao['regra_id'] for associacao in associacoes}
    
    # Filtrar regras que não estão associadas
    regras_nao_associadas = [regra for regra in regras if regra['id'] not in regras_associadas_ids]
    
    # Retornar para o template com as regras não associadas
    return render_template('regras_nao_associadas.html', regras_nao_associadas=regras_nao_associadas)



# Rota para adicionar regra
@app.route('/add_regra', methods=['GET', 'POST'])
def add_regra():
    if request.method == 'POST':
        nome = request.form['nome']
        query = request.form['query']
        
        # Verifica se já existe uma regra com o mesmo nome
        regras = load_data(REGRAS_FILE)
        if any(regra['nome'] == nome for regra in regras):
            return render_template('add_regra.html', error="Já existe uma regra com esse nome.")
        
        # Cria a nova regra
        regra_id = len(regras) + 1
        regras.append({'id': regra_id, 'nome': nome, 'query': query})
        save_data(REGRAS_FILE, regras)
        return redirect(url_for('list_regras'))
    
    return render_template('add_regra.html')


# Rota para editar regra
@app.route('/edit_regra/<int:id>', methods=['GET', 'POST'])
def edit_regra(id):
    regras = load_data(REGRAS_FILE)
    regra = next((r for r in regras if r['id'] == id), None)
    if request.method == 'POST':
        regra['nome'] = request.form['nome']
        regra['query'] = request.form['query']
        save_data(REGRAS_FILE, regras)
        return redirect(url_for('list_regras'))
    return render_template('edit_regra.html', regra=regra)

# Rota para deletar regra
@app.route('/delete_regra/<int:id>', methods=['POST'])
def delete_regra(id):
    regras = load_data(REGRAS_FILE)
    regras = [r for r in regras if r['id'] != id]
    save_data(REGRAS_FILE, regras)
    return redirect(url_for('list_regras'))

# Rota para listar associações
@app.route('/associacoes')
def list_associacoes():
    associacoes = load_data(ASSOCIACOES_FILE)
    empresas = load_data(EMPRESAS_FILE)
    regras = load_data(REGRAS_FILE)
    for associacao in associacoes:
        # associacao['id'] = next((e['nome'] for e in associacoes if e['id'] == associacao['associacao_id']), '')
        associacao['empresa_nome'] = next((e['nome'] for e in empresas if e['id'] == associacao['empresa_id']), '')
        associacao['regra_nome'] = next((r['nome'] for r in regras if r['id'] == associacao['regra_id']), '')
    return render_template('list_associacoes.html', associacoes=associacoes)

# Rota para adicionar associação
@app.route('/add_associacao', methods=['GET', 'POST'])
def add_associacao():
    empresas = load_data(EMPRESAS_FILE)
    regras = load_data(REGRAS_FILE)
    
    if request.method == 'POST':
        empresa_id = int(request.form['empresa_id'])
        regra_id = int(request.form['regra_id'])
        
        # Verifica se a associação já existe
        associacoes = load_data(ASSOCIACOES_FILE)
        if any(a['empresa_id'] == empresa_id and a['regra_id'] == regra_id for a in associacoes):
            return render_template('add_associacao.html', empresas=empresas, regras=regras, error="Essa empresa já está associada a essa regra.")
        
        # Cria a nova associação
        associacao_id = len(associacoes) + 1
        associacoes.append({'id': associacao_id, 'empresa_id': empresa_id, 'regra_id': regra_id})
        save_data(ASSOCIACOES_FILE, associacoes)
        return redirect(url_for('list_associacoes'))
    
    return render_template('add_associacao.html', empresas=empresas, regras=regras)


# Rota para deletar associação
@app.route('/delete_associacao/<int:empresa_id>/<int:regra_id>', methods=['POST'])
def delete_associacao(empresa_id, regra_id):
    associacoes = load_data(ASSOCIACOES_FILE)
    associacoes = [a for a in associacoes if not (a['empresa_id'] == empresa_id and a['regra_id'] == regra_id)]
    save_data(ASSOCIACOES_FILE, associacoes)
    return redirect(url_for('list_associacoes'))

if __name__ == '__main__':
    app.run(debug=True)
