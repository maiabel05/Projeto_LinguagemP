import tkinter as tk
from tkinter import ttk, messagebox

from database import inicializar_banco
from crud import (
    criar_midia,
    listar_status,
    buscar_por_id,
    atualizar_midia,
    excluir_midia,
)

FORMATOS = ["Livro", "Filme", "Série", "Anime", "Mangá", "HQ", "Desenho", "Outro"]
STATUS = ["Quero ver", "Em andamento", "Concluído", "Pausado", "Abandonado"]

class GerenciadorMidiasApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gerenciador de Mídias")
        self.root.geometry("1180x680")
        self.root.minsize(1000, 600)

        self.midia_selecionada_id: int | None = None
        self.tabela_por_status = dict[str, ttk.Treeview] = {}

        self.contruir_interface()
        self.recarregar_todas_abas()

    def contruir_interface(self):

        #Container principal
        main_frame = ttk.Frame(self.root, padding = 12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        #Painel formulário
        form_frame = ttk.LabelFrame(main_frame, text = "Detalhes da Mídia", padding = 12)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx = (0, 12))

        #Título
        ttk.Label(form_frame, text = "Título *:").grid(row = 0, column = 0, sticky = "w", padding = (0, 2))
        self.entry_titulo = ttk.Entry(form_frame, width = 38)
        self.entry_titulo.grid(row = 1, column = 0, columnspan = 2, sticky = "ew", pady = (0, 8))

        #Formato & Ano
        ttk.Label(form_frame, text = "Formato *:").grid(row = 2, column = 0, sticky = "w", padding = (0, 2))
        ttk.Label(form_frame, text = "Ano:").grid(row = 2, column = 1, sticky = "w", padx = (8, 0), pady = (0, 2))

        self.combo_formato = ttk.Combobox(form_frame, values = FORMATOS, state = "readonly", width = 16)
        self.combo_formato.set(FORMATOS[0])
        self.combo_formato.grid(row = 3, column = 0, sticky = "ew", pady = (0, 8))

        self.entry_ano = ttk.Entry(form_frame, width = 16)
        self.entry_ano.grid(row = 3, column = 1, sticky = "ew", padx = (8, 0), pady = (0, 8))

        #Autor/Diretor
        ttk.Label(form_frame, text = "Autor/Diretor:").grid(row = 4, column = 0, sticky = "w", padding = (0, 2))
        self.entry_autor = ttk.Entry(form_frame, width = 38)
        self.entry_autor.grid(row = 5, column = 0, columnspan = 2, sticky = "ew", pady = (0, 8))

        #Status & Nota
        ttk.Label(form_frame, text = "Status *:").grid(row = 6, column = 0, sticky = "w", padding = (0, 2))
        ttk.Label(form_frame, text = "Nota:").grid(row = 6, column = 1, sticky = "w", padx = (8, 0), pady = (0, 2))

        self.combo_status = ttk.Combobox(form_frame, values = STATUS, state = "readonly", width = 16)
        self.combo_status.set(STATUS[0])
        self.combo_status.grid(row = 7, column = 0, sticky = "ew", pady = (0, 8))

        self.entry_nota = ttk.Entry(form_frame, width = 16)
        self.entry_nota.grid(row = 7, column = 1, sticky = "ew", padx = (8, 0), pady = (0, 8))

        #Progresso
        ttk.Label(form_frame, text = "Progresso (EX: Ep. 5, Cap. 40, Vol. 12): ").grid(
            row = 8, column = 0, columnspan = 2, sticky = "w", padding = (0, 8))
        self.entry_progresso = ttk.Entry(form_frame, width = 38)

        #Resenha
        ttk.Label(form_frame, text = "Resenha Crítica (Opcional): ").grid(
            row = 10, column = 0, columnspan = 2, sticky = "w", padding = (0, 2))
        self.text_resenha = tk.Text(form_frame, width = 38, height = 8, wrap = tk.WORD, font = ("SEGOE UI", 9))
        self.text_resenha.grid(row = 11, column = 0, columnspan = 2, sticky = "nsew", pady = (0, 12))
        form_frame.rowconfigure(11, weight = 1)

        #Botões de Ação CRUD
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row = 12, column = 0, columnspan = 2, sticky = "ew")
        button_frame.columnconfigure((0, 1), weight = 1)
    
        self.button_salvar = ttk.Button(button_frame, text = "Criar novo", command = self.criar_midia)
        self.button_salvar.grid(row = 0, column = 0, sticky = "ew", padx = (0, 4), pady = (0, 6))

        self.button_atualizar = ttk.Button(
            button_frame, text = "Atualizar", command = self.atualizar_midia, state = tk.DISABLED)
        self.button_atualizar.grid(row = 0, column = 1, sticky = "ew", padx = (4, 0), pady = (0, 6))

        self.button_limpar = ttk.Button(button_frame, text="Limpar / Novo", command=self.limpar_formulario)
        self.button_limpar.grid(row=1, column=0, sticky="ew", padx=(0, 4))

        self.button_excluir = ttk.Button(
            button_frame, text="Excluir Obra", command=self.deletar_selecionado, state=tk.DISABLED)
        self.button_excluir.grid(row=1, column=1, sticky="ew", padx=(4, 0))

        #Painel: Busca e abas
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #Barra de busca
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady = (0, 8))

        ttk.Label(search_frame, text = "Buscar por título:").pack(side=tk.LEFT, padx = (0, 6))
        self.entry_busca = ttk.Entry(search_frame)
        self.entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx = (0, 6))
        self.entry_busca.bind("<KeyRelease>", lambda _: self.recarregar_todas_abas())

        ttk.Button(search_frame, text = "Limpar busca", command = self.limpar_busca).pack(side=tk.RIGHT)

        #Notebook com abas por status
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        colunas = ("ID", "Título", "Formato", "Ano", "Autor/Diretor", "Status", "Progresso", "Nota", "Resenha", "Atualizado em")

        for status in STATUS:
            aba = ttk.Frame(self.notebook, padding = 6)
            self.notebook.add(aba, text = status)

            tree = ttk.Treeview(aba, columns = colunas, show = "headings", selectmode = "browse")
            tree.heading ("ID", text = "ID")
            tree.heading ("Título", text = "Título")
            tree.heading ("Formato", text = "Formato")
            tree.heading ("Ano", text = "Ano")
            tree.heading ("Autor/Diretor", text = "Autor/Diretor")
            tree.heading ("Status", text = "Status")
            tree.heading ("Progresso", text = "Progresso")
            tree.heading ("Nota", text = "Nota")
            tree.heading ("Resenha", text = "Resenha")
            tree.heading ("Atualizado em", text = "Atualizado em")

            tree.column("ID", width = 40, anchor = "center")
            tree.column("Título", width = 220, anchor = "w")
            tree.column("Formato", width = 85, anchor = "center")
            tree.column("Ano", width = 60, anchor = "center")
            tree.column("Autor/Diretor", width = 150, anchor = "w")
            tree.column("Status", width = 120, anchor = "center")
            tree.column("Progresso", width = 110, anchor = "center")
            tree.column("Nota", width = 60, anchor = "center")
            tree.column("Resenha", width = 200, anchor = "w")
            tree.column("Atualizado em", width = 120, anchor = "center")

            scrollbar = ttk.Scrollbar(aba, orient = tk.VERTICAL, command = tree.yview)
            tree.configure(yscrollcommand = scrollbar.set)

            tree.pack(side = tk.LEFT, fill = tk.BOTH, expand=True)
            scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

            tree.bind("<<TreeviewSelect>>", lambda event, t = tree: self.ao_selecionar_item(t))
            self.tabela_por_status[status] = tree

    def _validar_campos(self):

        titulo = self.entry_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Erro", "O campo 'Título' é obrigatório.", "Informe o título  da obra.")
            return None

        formato = self.combo_formato.get()
        ano_str = self.entry_ano.get().strip()
        autor = self.entry_autor.get().strip()
        status = self.combo_status.get()
        progresso = self.entry_progresso.get().strip()
        nota_str = self.entry_nota.get().strip()
        resenha = self.text_resenha.get("1.0", tk.END).strip()
        atualizado_em = None  # Este campo será preenchido automaticamente pelo banco de dados

        # Validação do ano
        ano_str = self.entry_ano.get().strip()
        ano = None
        if ano_str:
            if not ano_str.isdigit() or len(ano_str) != 4:
                messagebox.showerror("Erro", "O campo 'Ano' deve ser um número de 4 dígitos.")
                return None
            ano_str = int(ano_str)

        # Validação da nota
        nota_str = self.entry_nota.get().strip()
        nota = None
        if nota_str:
            try:
                nota = float(nota_str)
                if nota < 0 or nota > 10:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Erro de Validação", "A nota deve ser um número entre 0 e 10.")
                return None
        return {
            "titulo": titulo,
            "formato": formato,
            "ano": ano,
            "autor": autor,
            "status": status,
            "progresso": progresso,
            "nota": nota,
            "resenha": resenha,
            "atualizado_em": atualizado_em
        }

    def salvar_novo(self):
        dados = self._validar_campos()
        if not dados:
            return

        criar_midia(**dados)
        self.recarregar_todas_abas()
        self._selecionar_aba_por_status(dados["status"])
        self.limpar_formulario()
        messagebox.showinfo("Sucesso", "Mídia criada com sucesso!")

    def salvar_edicao(self):
        if self.midia_selecionada_id is None:
            return
        dados = self._validar_campos()
        if not dados:
            return
        
        atualizar_midia(self.midia_selecionada_id, **dados)
        self.recarregar_todas_abas()
        self.selecionar_aba_por_status(dados["status"])
        self.limpar_formulario()
        messagebox.showinfo("Sucesso", "Mídia atualizada com sucesso!")
       # inicializar_banco()

    def deletar_selecionado(self):
        if self.midia_selecionada_id is None:
            return

        confirmar = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir a mídia selecionada? Esta ação não pode ser desfeita.")
        if confirmar:
            excluir_midia(self.midia_selecionada_id)
        self.recarregar_todas_abas()
        self.limpar_formulario()

    def ao_selecionar_item(self, tree: ttk.Treeview):
        selecao = tree.selection()
        if not selecao:
            return

        valores = tree.item(selecao[0], "values")
        midia_id = int(valores[0])
        midia = buscar_por_id(midia_id)

        if not midia:
            return

        self.midia_selecionada_id = midia["id"]

        #Preenche os campos do formulário com os dados da mídia selecionada
        self.entry_titulo.delete(0, tk.END)
        self.entry_titulo.insert(0, midia["titulo"])

        self.combo_formato.set(midia["formato"])

        self.entry_ano.delete(0, tk.END)
        if midia["ano"] is not None:
            self.entry_ano.insert(0, str(midia["ano"]))

        self.entry_autor.delete(0, tk.END)
        if midia["autor"] is not None:
            self.entry_autor.insert(0, midia["autor"])

        self.combo_status.set(midia["status"])

        self.entry_progresso.delete(0, tk.END)
        if midia["progresso"] is not None:
            self.entry_progresso.insert(0, midia["progresso"])

        self.entry_nota.delete(0, tk.END)
        if midia["nota"] is not None:
            self.entry_nota.insert(0, str(midia["nota"]))

        self.text_resenha.delete("1.0", tk.END)
        if midia["resenha"] is not None:
            self.text_resenha.insert(tk.END, midia["resenha"])

        #Habilita os botões de atualizar e excluir
        self.button_atualizar.config(state = tk.NORMAL)
        self.button_excluir.config(state = tk.NORMAL)

    def limpar_formulario(self):
        self.midia_selecionada_id = None
        self.entry_titulo.delete(0, tk.END)
        self.combo_formato.set(FORMATOS[0])
        self.entry_ano.delete(0, tk.END)
        self.entry_autor.delete(0, tk.END)
        self.combo_status.set(STATUS[0])
        self.entry_progresso.delete(0, tk.END)
        self.entry_nota.delete(0, tk.END)
        self.text_resenha.delete("1.0", tk.END)

        self.button_atualizar.config(state = tk.DISABLED)
        self.button_excluir.config(state = tk.DISABLED)

    #Limpa a seleção na tabela
        for tree in self.tabela_por_status.values():
            tree.selection_remove(tree.selection())

    def recarregar_todas_abas(self):
        termo = self.entry_busca.get()

        for idx, status in enumerate(STATUS):
            tree = self.tabela_por_status[status]
        for item in tree.get_children():
            tree.delete(item)

        registros = listar_status(status, termo)
        for row in registros:
            tree.insert("", tk.END, values = (
                row["id"],
                row["titulo"],
                row["formato"],
                row["ano"] if row["ano"] is not None else "",
                row["autor"] if row["autor"] is not None else "",
                row["status"],
                row["progresso"] if row["progresso"] is not None else "",
                row["nota"] if row["nota"] is not None else "",
                row["resenha"] if row["resenha"] is not None else "",
                row["atualizado_em"]
            ))

        #Atualiza a aba do notebook com o número de registros
        self.notebook.tab(idx, text = f"{status} ({len(registros)})")

    def _selecionar_aba_por_status(self, status: str):
        if status in STATUS:
            index = STATUS.index(status)
            self.notebook.select(index)

    def limpar_busca(self):
        self.entry_busca.delete(0, tk.END)
        self.recarregar_todas_abas()

if __name__ == "__main__":
    inicializar_banco()
    root = tk.Tk()
    app = GerenciadorMidiasApp(root)
    root.mainloop()
