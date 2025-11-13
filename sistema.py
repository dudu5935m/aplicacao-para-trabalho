import pyodbc # Importa biblioteca para conexão com o banco de dados
import tkinter as tk # Importa biblioteca para interface gráfica
from tkinter import ttk, messagebox # Importa componentes da interface gráfica
from decimal import Decimal # Importa tipo Decimal para manipulação de valores monetários >= <=
from PIL import Image, ImageTk
from datetime import datetime

 # Carrega imagem de fundo

USUARIO_CORRETO = "Eduardo" # Define usuário correto
SENHA_CORRETA = "ed24ar03" # Define senha correta


def conectar_banco(): # Função para conectar ao banco de dados
    try: # Tenta estabelecer a conexão com o banco de dados
        conexao = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=10.64.46.26;'
            'DATABASE=ControleEstoque;'
            'UID=sa;'
            'PWD=1234567890'
        ) # Estabelece a conexão com o banco de dados
        return conexao
    except pyodbc.Error as erro:
        messagebox.showerror("Erro de conexão", f"{erro}") # Exibe erro de conexão
        return None

def cadastrar_categoria(nome_categoria):
    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("INSERT INTO Categorias (nome_categoria) VALUES (?)", (nome_categoria,))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Categoria cadastrada com sucesso!")
        except pyodbc.Error as erro:
            messagebox.showerror("Erro", f"Erro ao cadastrar categoria:\n{erro}")
        finally:
            conexao.close()

def cadastrar_produto(nome, descricao, preco, quantidade, estoque_minimo, id_categoria):
    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()

            # Verifica se o produto já existe pelo nome
            cursor.execute("SELECT id_produto, quantidade_estoque FROM Produtos WHERE nome_produto = ?", (nome,))
            resultado = cursor.fetchone()

            if resultado:
                id_existente, qtd_atual = resultado
                nova_qtd = qtd_atual + quantidade
                cursor.execute("UPDATE Produtos SET quantidade_estoque = ? WHERE id_produto = ?", (nova_qtd, id_existente))
            else:
                # Produto novo, insere normalmente
                sql = """
                    INSERT INTO Produtos (
                        nome_produto, descricao, preco,
                        quantidade_estoque, estoque_minimo, id_categoria
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """
                dados = (nome, descricao, preco, quantidade, estoque_minimo, id_categoria)
                cursor.execute(sql, dados)

            conexao.commit()

        except pyodbc.Error as erro:
            raise Exception(f"Erro ao cadastrar produto:\n{erro}")
        finally:
            conexao.close()

def registrar_saida(id_produto, quantidade_saida, responsavel):
    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT quantidade_estoque FROM Produtos WHERE id_produto = ?", (id_produto,))
            resultado = cursor.fetchone()
            if not resultado:
                raise Exception("Produto não encontrado.")
            estoque_atual = resultado[0]
            if quantidade_saida > estoque_atual:
                raise Exception("Quantidade insuficiente em estoque.")
            novo_estoque = estoque_atual - quantidade_saida
            cursor.execute("UPDATE Produtos SET quantidade_estoque = ? WHERE id_produto = ?", (novo_estoque, id_produto))
            cursor.execute("""
                INSERT INTO Movimentacoes (id_produto, tipo, quantidade, responsavel)
                VALUES (?, 'saida', ?, ?)
            """, (id_produto, quantidade_saida, responsavel))
            conexao.commit()
            print("✅ Venda registrada com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            conexao.close()

def obter_categorias():
    conexao = conectar_banco()
    categorias = {}
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_categoria, nome_categoria FROM Categorias")
            resultado = cursor.fetchall()
            categorias = {nome: id_ for id_, nome in resultado}
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar categorias:\n{e}")
        finally:
            conexao.close()
    return categorias

def buscar_id_produto_por_nome(nome_produto):
    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_produto FROM Produtos WHERE nome_produto = ?", (nome_produto,))
            resultado = cursor.fetchone()
            if resultado:
                return resultado[0]
            else:
                return None
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar produto:\n{e}")
        finally:
            conexao.close()
    return None

def buscar_id_categoria_por_nome(nome_categoria):
    conexao = conectar_banco()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_categoria FROM Categorias WHERE nome_categoria = ?", (nome_categoria,))
            resultado = cursor.fetchone()
            if resultado:
                return resultado[0]
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar categoria:\n{e}")
        finally:
            conexao.close()
    return None

def obter_produtos():
    conexao = conectar_banco()
    produtos = {}
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute("SELECT id_produto, nome_produto FROM Produtos")
            resultado = cursor.fetchall()
            produtos = {nome: id_ for id_, nome in resultado}
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos:\n{e}")
        finally:
            conexao.close()
    return produtos

def abrir_sistema():
    # Criação da interface
    janela = tk.Tk()
    janela.title("📦 Sistema de Estoque")
    janela.geometry
    janela.config(bg="#f0f4f8")

    # Estilo ttk
    style = ttk.Style(janela)
    style.theme_use('clam')
    style.configure('TNotebook', background='#e3eafc', borderwidth=0)
    style.configure('TNotebook.Tab', font=('Segoe UI', 12, 'bold'), padding=[12, 8])
    style.map('TNotebook.Tab', background=[('selected', '#b6ccfe')])
    style.configure('TButton', font=('Segoe UI', 12, 'bold'), background='#4f8cff', foreground='white', padding=8)
    style.map('TButton', background=[('active', '#2563eb')])
    style.configure('Custom.TEntry',
        foreground='#22223b',
        fieldbackground='#f7f7ff',
        bordercolor='#4f8cff',
        borderwidth=2,
        relief='flat',
        padding=8,
        font=('Segoe UI', 12)
    )

    abas = ttk.Notebook(janela)
    abas.pack(expand=1, fill="both", padx=10, pady=10)

    # Aba Categoria
    aba_cat = tk.Frame(abas, bg="#DCEAF9")
    abas.add(aba_cat, text="Cadastrar Categoria")
    tk.Label(aba_cat, text="Nome da Categoria:", bg="#DCEAF9", font=("Segoe UI", 12, "bold")).pack(pady=12)
    entry_categoria = ttk.Entry(aba_cat, width=40, style='Custom.TEntry')
    entry_categoria.pack(pady=7)
    btn_cat = ttk.Button(aba_cat, text="Salvar Categoria", command=lambda: cadastrar_categoria(entry_categoria.get()))
    btn_cat.pack(pady=18)

    # Aba Produto
    aba_prod = tk.Frame(abas, bg="#F2E9F9")
    abas.add(aba_prod, text="Cadastrar Produto")

    labels = ["Nome", "Descrição", "Preço", "Quantidade", "Estoque mínimo"]
    entries = []
    for texto in labels:
        tk.Label(aba_prod, text=texto + ":", bg="#F2E9F9", font=("Segoe UI", 12, "bold")).pack(pady=8)
        campo = ttk.Entry(aba_prod, width=40, style="Custom.TEntry", font=("Segoe UI", 11))
        campo.pack(pady=4)
        entries.append(campo)
    entry_nome, entry_desc, entry_preco, entry_qtd, entry_min = entries

    # Combobox para categoria
    tk.Label(aba_prod, text="Categoria:", bg="#F2E9F9", font=("Segoe UI", 12, "bold")).pack(pady=8)
    categorias_dict = obter_categorias()
    combo_categoria = ttk.Combobox(
        aba_prod,
        values=list(categorias_dict.keys()),
        state="readonly",
        font=("Segoe UI", 11),
        width=40,
        justify="center"
    )
    combo_categoria.pack(pady=4)

    # ---> Definir função aqui, usando as entradas locais
    def obter_dados_produtos():
        try:
            nome = entry_nome.get()
            descricao = entry_desc.get()
            preco_str = entry_preco.get()
            quantidade_str = entry_qtd.get()
            estoque_minimo_str = entry_min.get()
            categoria_nome = combo_categoria.get()
            id_categoria = buscar_id_categoria_por_nome(categoria_nome) if categoria_nome else None

            if not preco_str:
                raise Exception("O campo Preço é obrigatório.")

            preco = float(preco_str)
            quantidade = int(quantidade_str) if quantidade_str else 0
            estoque_minimo = int(estoque_minimo_str) if estoque_minimo_str else 0

            cadastrar_produto(nome, descricao, preco, quantidade, estoque_minimo, id_categoria)
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")

            for campo in (entry_nome, entry_desc, entry_preco, entry_qtd, entry_min):
                campo.delete(0, tk.END)
            combo_categoria.set("")

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    btn_prod = ttk.Button(
        aba_prod,
        text="Salvar Produto",
        command=obter_dados_produtos
    )
    btn_prod.pack(pady=18)

    # Aba Registrar Venda
    aba_venda = tk.Frame(abas, bg="#E6F2E6")
    abas.add(aba_venda, text="Registrar Venda")

    tk.Label(
        aba_venda, text="Produto:", bg="#E6F2E6",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=12)
    produtos_dict = obter_produtos()
    combo_produto = ttk.Combobox(
        aba_venda,
        values=list(produtos_dict.keys()),
        state="readonly",
        font=("Segoe UI", 11),
        width=40,
        justify="center"
    )
    combo_produto.pack(pady=7)

    tk.Label(
        aba_venda, text="Quantidade Vendida:", bg="#E6F2E6",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=12)
    entry_qtd_venda = ttk.Entry(
        aba_venda, width=40, style="Custom.TEntry",
        font=("Segoe UI", 11), justify="center"
    )
    entry_qtd_venda.pack(pady=7)

    tk.Label(
        aba_venda, text="Responsável:", bg="#E6F2E6",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=12)
    entry_resp_venda = ttk.Entry(
        aba_venda, width=40, style="Custom.TEntry",
        font=("Segoe UI", 11), justify="center"
    )
    entry_resp_venda.pack(pady=7)

    def obter_dados_venda():
        try:
            nome_produto = combo_produto.get()
            id_produto = produtos_dict.get(nome_produto)
            if id_produto is None:
                raise Exception("Selecione um produto válido.")

            quantidade_saida = int(entry_qtd_venda.get())
            responsavel = entry_resp_venda.get()
            registrar_saida(id_produto, quantidade_saida, responsavel)
            messagebox.showinfo("Sucesso", "✅ Venda registrada com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Dados inválidos: {e}")

    btn_venda = ttk.Button(
        aba_venda,
        text="Registrar Venda",
        command=obter_dados_venda
    )
    btn_venda.pack(pady=18)

    # Aba Visualizar Produtos
    aba_visualizar = tk.Frame(abas, bg="#F9F9F9")
    abas.add(aba_visualizar, text="Visualizar Produtos")

    colunas = (
        "id_produto", "nome_produto", "descricao",
        "preco", "quantidade_estoque", "estoque_minimo", "id_categoria"
    )

    tree = ttk.Treeview(aba_visualizar, columns=colunas, show="headings", height=15)

    # Define títulos e larguras das colunas
    tree.heading("id_produto", text="ID")
    tree.column("id_produto", anchor="center", width=50)

    tree.heading("nome_produto", text="Nome do Produto")
    tree.column("nome_produto", anchor="w", width=500)

    tree.heading("descricao", text="Descrição")
    tree.column("descricao", anchor="w", width=300)

    tree.heading("preco", text="Preço")
    tree.column("preco", anchor="center", width=80)

    tree.heading("quantidade_estoque", text="Qtd. Estoque")
    tree.column("quantidade_estoque", anchor="center", width=110)

    tree.heading("estoque_minimo", text="Estoque Mínimo")
    tree.column("estoque_minimo", anchor="center", width=110)

    tree.heading("id_categoria", text="ID Categoria")
    tree.column("id_categoria", anchor="center", width=90)

    tree.column("nome_produto", anchor="w")
    tree.column("descricao", anchor="w")

    tree.pack(expand=True, fill="both", padx=10, pady=10)

    def carregar_produtos():
        for item in tree.get_children():
            tree.delete(item)

        conexao = conectar_banco()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("""
                    SELECT id_produto, nome_produto, descricao, preco, 
                           quantidade_estoque, estoque_minimo, id_categoria
                    FROM Produtos
                """)
                for row in cursor.fetchall():
                    valores_formato = tuple(
                        str(item) if isinstance(item, (int, float, Decimal)) else item
                        for item in row
                    )
                    if len(row) == 7:  # Garante que só insere linhas completas
                        tree.insert("", "end", values=valores_formato)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar produtos:\n{e}")
            finally:
                conexao.close()

    btn_atualizar = ttk.Button(aba_visualizar, text="Atualizar Lista", command=carregar_produtos)
    btn_atualizar.pack(pady=8)

    carregar_produtos()

    # Aba Visualizar Movimentações
    aba_mov = tk.Frame(abas, bg="#f5f5f5")
    abas.add(aba_mov, text="Movimentações")

    # Estilo personalizado da Treeview
    style = ttk.Style()
    style.configure("Custom.Treeview", 
                    borderwidth=1, 
                    relief="solid", 
                    font=("Segoe UI", 9))

    tree_mov = ttk.Treeview(
        aba_mov,
        columns=(
            "id_movimentacao", "id_produto", "tipo",
            "quantidade", "data_movimentacao", "responsavel"
        ),
        show="headings",
        height=15,
        style="Custom.Treeview"
    )

    # Definições de títulos e larguras personalizadas
    colunas_mov = {
        "id_movimentacao": "ID",
        "id_produto": "ID Produto",
        "tipo": "Tipo",
        "quantidade": "Qtd",
        "data_movimentacao": "Data",
        "responsavel": "Responsável"
    }

    larguras = {
        "id_movimentacao": 60,
        "id_produto": 80,
        "tipo": 80,
        "quantidade": 70,
        "data_movimentacao": 110,
        "responsavel": 130
    }

    for col, texto in colunas_mov.items():
        tree_mov.heading(col, text=texto)
        tree_mov.column(col, anchor="center", width=larguras[col])

    tree_mov.pack(expand=True, fill="both", padx=5, pady=5)

    # Função para carregar os dados
    def carregar_movimentacoes():
        for item in tree_mov.get_children():
            tree_mov.delete(item)

        conexao = conectar_banco()
        if conexao:
            try:
                cursor = conexao.cursor()
                cursor.execute("""
                    SELECT id_movimentacao, id_produto, tipo, quantidade,
                           data_movimentacao, responsavel
                    FROM Movimentacoes
                    ORDER BY data_movimentacao DESC
                """)
                for row in cursor.fetchall():
                    id_mov, id_produto, tipo, qtd, data_raw, responsavel = row
                    if isinstance(data_raw, datetime):
                        data_formatada = data_raw.strftime("%d/%m/%Y")
                    else:
                        data_formatada = str(data_raw)
                    
                    tree_mov.insert("", "end", values=(
                        id_mov, id_produto, tipo, qtd, data_formatada, responsavel
                    ))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar movimentações:\n{e}")
            finally:
                conexao.close()

    # Botão de atualização
    btn_atualizar_mov = ttk.Button(aba_mov, text="Atualizar Lista", command=carregar_movimentacoes)
    btn_atualizar_mov.pack(pady=4)

    # Carregamento inicial
    carregar_movimentacoes()

    # Adicione outros elementos/abas conforme necessário

    janela.mainloop()

# Tela de login estilizada
login_janela = tk.Tk()
login_janela.title("Login")
login_janela.geometry("350x320")
login_janela.bind("<Return>", lambda event: fazer_login())
login_janela.resizable(False, False)
login_janela.configure(bg="#e3eafc")

frame = tk.Frame(login_janela, bg="#f7f7ff", bd=2, relief="groove")
frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=250)

tk.Label(frame, text="Bem-vindo!", font=("Cambria", 16, "bold"), bg="#f7f7ff", fg="#2563eb").pack(pady=(10, 2))
tk.Label(frame, text="Faça login para acessar", font=("Cambria", 10), bg="#f7f7ff", fg="#22223b").pack(pady=(0, 10))

tk.Label(frame, text="Usuário:", font=("Segoe UI", 11), bg="#f7f7ff").pack(anchor="w", padx=25)
entry_usuario = tk.Entry(frame, font=("Segoe UI", 11), bd=1, relief="solid", justify="center")
entry_usuario.pack(padx=25, pady=3, fill="x")

tk.Label(frame, text="Senha:", font=("Segoe UI", 11), bg="#f7f7ff").pack(anchor="w", padx=25)
entry_senha = tk.Entry(frame, show="*", font=("Segoe UI", 11), bd=1, relief="solid", justify="center")
entry_senha.pack(padx=25, pady=3, fill="x")
def fazer_login():

    usuario = entry_usuario.get()
    senha = entry_senha.get()
    if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
        messagebox.showinfo("Login", "Login realizado com sucesso!")
        login_janela.destroy()  # Fecha a janela de login
        abrir_sistema()  # Abre o sistema principal
    else:
        messagebox.showerror("Erro", "Usuário ou senha incorretos.")
btn_login = tk.Button(
    frame, text="Entrar", font=("Segoe UI", 12, "bold"),
    bg="#4f8cff", fg="white", activebackground="#2563eb", activeforeground="white",
    relief="flat", command=fazer_login
)
btn_login.pack(pady=12, ipadx=10, ipady=2)

login_janela.mainloop()