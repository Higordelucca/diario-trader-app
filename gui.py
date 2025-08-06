import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox
from datetime import date, datetime
import data_manager
import analytics
import api_service

class TradingJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diário de Trader - v2.2 (Final)")
        self.root.geometry("950x700") # Aumentei um pouco a largura para os botões

        # --- Frames Principais ---
        dashboard_frame = ttk.Frame(self.root, padding="10", bootstyle="secondary")
        dashboard_frame.pack(fill=X, side=TOP, padx=10, pady=(10,0))
        
        filter_frame = ttk.Frame(self.root, padding="10")
        filter_frame.pack(fill=X, side=TOP, padx=10)
        
        form_frame = ttk.Frame(self.root, padding="10")
        form_frame.pack(fill=X, side=TOP, padx=10)

        tree_frame = ttk.Frame(self.root, padding="10")
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=(0,10))

        # --- Widgets do Filtro (com layout Grid) ---
        ttk.Label(filter_frame, text="Ativo:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        ttk.Label(filter_frame, text="Data Início:").grid(row=0, column=1, padx=5, sticky="w")
        ttk.Label(filter_frame, text="Data Fim:").grid(row=0, column=2, padx=5, sticky="w")

        self.filtro_ativo_entry = ttk.Entry(filter_frame)
        self.filtro_ativo_entry.grid(row=1, column=0, padx=(0, 5), sticky="ew")

        self.filtro_data_inicio = DateEntry(filter_frame, dateformat="%Y-%m-%d")
        self.filtro_data_inicio.grid(row=1, column=1, padx=5, sticky="ew")
        self.filtro_data_inicio.entry.delete(0, END)

        self.filtro_data_fim = DateEntry(filter_frame, dateformat="%Y-%m-%d")
        self.filtro_data_fim.grid(row=1, column=2, padx=5, sticky="ew")
        self.filtro_data_fim.entry.delete(0, END)

        filtrar_btn = ttk.Button(filter_frame, text="Filtrar", command=self._aplicar_filtro, bootstyle="info")
        filtrar_btn.grid(row=1, column=3, padx=5, sticky="ew")

        limpar_btn = ttk.Button(filter_frame, text="Limpar", command=self._limpar_filtro, bootstyle="secondary")
        limpar_btn.grid(row=1, column=4, padx=5, sticky="ew")

        self.delete_btn = ttk.Button(filter_frame, text="Deletar", command=self._deletar_trade_selecionado, bootstyle="danger", state="disabled")
        self.delete_btn.grid(row=1, column=5, padx=15, sticky="ew")

        self._criar_dashboard(dashboard_frame)

        # --- Formulário de entrada ---
        self.entries = {}
        # ... (código do formulário continua igual)
        fields = {"Data:": {"key": "data"},"Horário:": {"key": "horario"},"Ativo:": {"key": "ativo"}, "Tipo (Compra/Venda):": {"key": "tipo_operacao"}, "Resultado:": {"key": "resultado_tipo"},"Valor Financeiro (US$):": {"key": "resultado_financeiro"}}
        i=0
        for label_text, config in fields.items():
            ttk.Label(form_frame, text=label_text).grid(row=0, column=i, sticky=W, padx=5); key = config["key"]
            if key == "resultado_tipo": widget = ttk.Combobox(form_frame, values=["Gain", "Loss"], width=10, state="readonly"); widget.current(0)
            else: widget = ttk.Entry(form_frame, width=15)
            self.entries[key] = widget; widget.grid(row=1, column=i, sticky=EW, padx=5); i += 1
        save_button = ttk.Button(form_frame, text="Salvar", command=self._salvar_trade, bootstyle="primary"); save_button.grid(row=0, column=i, rowspan=2, sticky="ns", padx=10)
        self.entries['data'].insert(0, date.today().strftime('%Y-%m-%d')); self.entries['horario'].insert(0, datetime.now().strftime('%H:%M:%S'))

        # --- Inicialização da Tabela e dos Dados ---
        self._criar_tabela(tree_frame)
        self.atualizar_dados()

    def _criar_dashboard(self, parent_frame):
        ttk.Label(parent_frame, text="SALDO TOTAL", font=("-size 10")).grid(row=0, column=0, padx=20, pady=(5,0)); ttk.Label(parent_frame, text="OPERAÇÕES TOTAIS", font=("-size 10")).grid(row=0, column=1, padx=20, pady=(5,0)); ttk.Label(parent_frame, text="TAXA DE ACERTO", font=("-size 10")).grid(row=0, column=2, padx=20, pady=(5,0)); self.saldo_label = ttk.Label(parent_frame, text="US$ 0.00", font=("-size 14 -weight bold"), bootstyle="success"); self.saldo_label.grid(row=1, column=0, padx=20, pady=(0,10)); self.total_ops_label = ttk.Label(parent_frame, text="0", font=("-size 14 -weight bold")); self.total_ops_label.grid(row=1, column=1, padx=20, pady=(0,10)); self.taxa_acerto_label = ttk.Label(parent_frame, text="0.00%", font=("-size 14 -weight bold")); self.taxa_acerto_label.grid(row=1, column=2, padx=20, pady=(0,10)); parent_frame.grid_columnconfigure((0,1,2), weight=1)
        ttk.Label(parent_frame, text="SALDO CONVERTIDO (BRL)", font=("-size 10")).grid(row=0, column=3, padx=20, pady=(5,0))

        self.saldo_brl_label = ttk.Label(parent_frame, text="R$ 0.00", font=("-size 14 -weight bold"), bootstyle="primary")
        self.saldo_brl_label.grid(row=1, column=3, padx=20, pady=(0,10))
        
        parent_frame.grid_columnconfigure((0,1,2,3), weight=1)
    
    def _atualizar_dashboard(self, trades):
        metricas = analytics.calcular_metricas(trades)
        saldo_usd = metricas['saldo_total']

        # Atualiza o saldo em USD
        saldo_style = "success" if saldo_usd >= 0 else "danger"
        self.saldo_label.config(text=f"$ {saldo_usd:.2f}", bootstyle=saldo_style) # Mudei para $

        # Atualiza as outras métricas
        self.total_ops_label.config(text=f"{metricas['total_operacoes']}")
        self.taxa_acerto_label.config(text=f"{metricas['taxa_acerto']:.2f}%")

        # --- LÓGICA NOVA PARA BRL ---
        taxa_cambio = api_service.obter_taxa_cambio_usd_brl()

        if taxa_cambio is not None:
            saldo_brl = saldo_usd * taxa_cambio
            self.saldo_brl_label.config(text=f"R$ {saldo_brl:.2f}")
        else:
            # Caso ocorra erro na API, exibe uma mensagem
            self.saldo_brl_label.config(text="Cotação N/A", bootstyle="warning")

    def _criar_tabela(self, parent_frame):
        colunas = ('id', 'data', 'horario', 'ativo', 'tipo_operacao', 'resultado_tipo', 'resultado_financeiro'); self.tree = ttk.Treeview(parent_frame, columns=colunas, show='headings', bootstyle="primary"); self.tree.configure(displaycolumns=('data', 'horario', 'ativo', 'tipo_operacao', 'resultado_tipo', 'resultado_financeiro')); headings_texts = ['ID', 'Data', 'Horário', 'Ativo', 'Tipo', 'Resultado', 'Valor (US$)']; column_widths = [40, 100, 80, 100, 100, 80, 100]
        for i, col in enumerate(colunas): self.tree.heading(col, text=headings_texts[i]); self.tree.column(col, width=column_widths[i], anchor=CENTER)
        scrollbar = ttk.Scrollbar(parent_frame, orient=VERTICAL, command=self.tree.yview); self.tree.configure(yscroll=scrollbar.set); scrollbar.pack(side=RIGHT, fill=Y); self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.tree.bind('<<TreeViewSelect>>', self._on_trade_select)

    def _popular_tabela(self, trades):
        self.delete_btn.config(state="disabled")
        for row in self.tree.get_children(): self.tree.delete(row)
        for i, trade in enumerate(trades): valores = [trade.get(col, '') for col in self.tree['columns']]; tag = 'oddrow' if i % 2 == 0 else 'evenrow'; self.tree.insert('', END, values=valores, tags=(tag,))
        self.tree.tag_configure('oddrow', background=None); self.tree.tag_configure('evenrow', background='#f0f0f0')

        self.tree.bind('<ButtonRelease-1>', self._on_trade_select)

    def atualizar_dados(self, filtro_ativo=None, data_inicio=None, data_fim=None):
        trades = data_manager.carregar_trades(filtro_ativo=filtro_ativo, data_inicio=data_inicio, data_fim=data_fim); self._popular_tabela(trades); self._atualizar_dashboard(trades)

    def _salvar_trade(self):
        trade_data = {};
        for key, widget in self.entries.items(): trade_data[key] = widget.get()
        if trade_data.get('ativo'): trade_data['ativo'] = trade_data['ativo'].upper().strip()
        if not trade_data.get('ativo') or not trade_data.get('resultado_financeiro'): messagebox.showerror("Erro de Validação", "Os campos 'Ativo' e 'Valor Financeiro' são obrigatórios."); return
        try:
            data_manager.salvar_trade(trade_data); messagebox.showinfo("Sucesso", "Operação salva com sucesso!"); self._limpar_campos()
            self.atualizar_dados(filtro_ativo=self.filtro_ativo_entry.get(), data_inicio=self.filtro_data_inicio.entry.get(), data_fim=self.filtro_data_fim.entry.get())
        except Exception as e: messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro inesperado:\n{e}")

    def _limpar_campos(self):
        keys_to_clear = ['ativo', 'tipo_operacao', 'resultado_financeiro'];
        for key in keys_to_clear: self.entries[key].delete(0, END)
        self.entries['horario'].delete(0, END); self.entries['horario'].insert(0, datetime.now().strftime('%H:%M:%S')); self.entries['resultado_tipo'].current(0)

    def _aplicar_filtro(self):
        filtro_ativo = self.filtro_ativo_entry.get().strip(); data_inicio = self.filtro_data_inicio.entry.get(); data_fim = self.filtro_data_fim.entry.get()
        self.atualizar_dados(filtro_ativo=filtro_ativo if filtro_ativo else None, data_inicio=data_inicio if data_inicio else None, data_fim=data_fim if data_fim else None)

    def _limpar_filtro(self):
        self.filtro_ativo_entry.delete(0, END); self.filtro_data_inicio.entry.delete(0, END); self.filtro_data_fim.entry.delete(0, END); self.atualizar_dados()

    def _deletar_trade_selecionado(self):
        selected_item = self.tree.focus();
        if not selected_item: messagebox.showwarning("Nenhuma seleção", "Por favor, selecione um trade na tabela para deletar."); return
        trade_values = self.tree.item(selected_item, 'values'); trade_id = trade_values[0]
        resposta = messagebox.askyesno("Confirmar Deleção", f"Você tem certeza que deseja deletar o trade ID {trade_id} permanentemente?")
        if resposta: data_manager.deletar_trade(trade_id); self.atualizar_dados(filtro_ativo=self.filtro_ativo_entry.get(), data_inicio=self.filtro_data_inicio.entry.get(), data_fim=self.filtro_data_fim.entry.get())

    def _on_trade_select(self, event):
        if self.tree.focus(): self.delete_btn.config(state="normal")
        else: self.delete_btn.config(state="disabled")

def main():
    data_manager.inicializar_banco()
    root = ttk.Window(themename="litera")
    app = TradingJournalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()