import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox
from datetime import date, datetime
import data_manager
import analytics
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import api_service

# Dicionário com os valores por ponto dos principais ativos
VALORES_POR_PONTO = {
    "Micro E-mini Dow (MYM)": 0.50,
    "Micro E-mini S&P 500 (MES)": 5.00,
    "Micro E-mini Nasdaq (MNQ)": 2.00,
    "E-mini Dow (YM)": 5.00,
    "E-mini S&P 500 (ES)": 50.00,
    "E-mini Nasdaq (NQ)": 20.00,
    "Micro Ouro (MGC)": 1.0,
    "Ouro (GC)": 10.0,
}

class TradingJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Diário de Trader - v3.0")
        self.root.geometry("1100x750")

        # --- Abas ---
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.tab1 = ttk.Frame(notebook, padding=10)
        self.tab2 = ttk.Frame(notebook, padding=10)
        notebook.add(self.tab1, text='Registro & Trades')
        notebook.add(self.tab2, text='Gráfico de Performance')
        
        # --- Estrutura de frames DENTRO da Aba 1 ---
        dashboard_frame = ttk.Frame(self.tab1, bootstyle="secondary")
        dashboard_frame.pack(fill=X, side=TOP, pady=(0,10))
        risk_frame = ttk.Labelframe(self.tab1, text="Gerenciamento de Risco & Posição", padding=10)
        risk_frame.pack(fill=X, side=TOP, pady=5)
        filter_frame = ttk.Frame(self.tab1)
        filter_frame.pack(fill=X, side=TOP, pady=5)
        form_frame = ttk.Frame(self.tab1)
        form_frame.pack(fill=X, side=TOP, pady=10)
        tree_frame = ttk.Frame(self.tab1)
        tree_frame.pack(fill=BOTH, expand=True)

        # --- Widgets ---
        self._criar_dashboard(dashboard_frame)
        self._criar_calculadora_risco(risk_frame)
        self._criar_filtros(filter_frame)
        self._criar_formulario_entrada(form_frame)
        self._criar_tabela(tree_frame)
        self._criar_grafico(self.tab2)
        
        self.id_em_edicao = None
        self.atualizar_dados()

    def _criar_dashboard(self, parent_frame):
        # ... (código existente)
        ttk.Label(parent_frame, text="SALDO TOTAL ($)", font=("-size 10")).grid(row=0, column=0, padx=10, pady=(5,0))
        self.saldo_label = ttk.Label(parent_frame, text="$ 0.00", font=("-size 14 -weight bold"), bootstyle="success")
        self.saldo_label.grid(row=1, column=0, padx=10, pady=(0,10))
        
        ttk.Label(parent_frame, text="SALDO (BRL)", font=("-size 10")).grid(row=0, column=1, padx=10, pady=(5,0))
        self.saldo_brl_label = ttk.Label(parent_frame, text="R$ 0.00", font=("-size 14 -weight bold"), bootstyle="primary")
        self.saldo_brl_label.grid(row=1, column=1, padx=10, pady=(0,10))
        
        ttk.Label(parent_frame, text="OPERAÇÕES TOTAIS", font=("-size 10")).grid(row=0, column=2, padx=10, pady=(5,0))
        self.total_ops_label = ttk.Label(parent_frame, text="0", font=("-size 14 -weight bold"))
        self.total_ops_label.grid(row=1, column=2, padx=10, pady=(0,10))
        
        ttk.Label(parent_frame, text="TAXA DE ACERTO", font=("-size 10")).grid(row=0, column=3, padx=10, pady=(5,0))
        self.taxa_acerto_label = ttk.Label(parent_frame, text="0.00%", font=("-size 14 -weight bold"))
        self.taxa_acerto_label.grid(row=1, column=3, padx=10, pady=(0,10))
        
        ttk.Label(parent_frame, text="PAYOFF RATIO", font=("-size 10")).grid(row=0, column=4, padx=10, pady=(5,0))
        self.payoff_label = ttk.Label(parent_frame, text="0.00", font=("-size 14 -weight bold"), bootstyle="info")
        self.payoff_label.grid(row=1, column=4, padx=10, pady=(0,10))
        
        parent_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

    def _criar_calculadora_risco(self, parent_frame):
        # ... (código existente)
        ttk.Label(parent_frame, text="Patrimônio Total ($):").grid(row=0, column=0, padx=5, pady=2, sticky="w"); self.patrimonio_entry = ttk.Entry(parent_frame, width=15); self.patrimonio_entry.grid(row=0, column=1, padx=5, pady=2)
        usar_saldo_btn = ttk.Button(parent_frame, text="Usar Saldo", command=self._preencher_patrimonio_com_saldo, bootstyle="outline-secondary"); usar_saldo_btn.grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(parent_frame, text="Risco / Operação (%):").grid(row=1, column=0, padx=5, pady=2, sticky="w"); self.risco_percent_entry = ttk.Entry(parent_frame, width=15); self.risco_percent_entry.grid(row=1, column=1, padx=5, pady=2); self.risco_percent_entry.insert(0, "1.0")
        ttk.Label(parent_frame, text="Preço de Entrada:").grid(row=0, column=3, padx=5, pady=2, sticky="w"); self.entrada_entry = ttk.Entry(parent_frame, width=15); self.entrada_entry.grid(row=0, column=4, padx=5, pady=2)
        ttk.Label(parent_frame, text="Preço do Stop Loss:").grid(row=1, column=3, padx=5, pady=2, sticky="w"); self.stop_entry = ttk.Entry(parent_frame, width=15); self.stop_entry.grid(row=1, column=4, padx=5, pady=2)
        ttk.Label(parent_frame, text="Selecionar Ativo:").grid(row=0, column=5, padx=5, pady=2, sticky="w"); self.ativo_calculadora_combo = ttk.Combobox(parent_frame, values=list(VALORES_POR_PONTO.keys()), state="readonly"); self.ativo_calculadora_combo.grid(row=0, column=6, padx=5, pady=2, sticky="ew"); self.ativo_calculadora_combo.bind("<<ComboboxSelected>>", self._on_asset_select)
        ttk.Label(parent_frame, text="Valor do Ponto ($):").grid(row=1, column=5, padx=5, pady=2, sticky="w"); self.valor_ponto_entry = ttk.Entry(parent_frame, width=15, state="readonly"); self.valor_ponto_entry.grid(row=1, column=6, padx=5, pady=2)
        calcular_risco_btn = ttk.Button(parent_frame, text="Calcular", command=self._calcular_risco, bootstyle="info"); calcular_risco_btn.grid(row=0, column=7, rowspan=2, padx=10, pady=5, sticky="ns")
        ttk.Label(parent_frame, text="Perda Máxima ($):", font=("-size 10")).grid(row=0, column=8, padx=10, pady=2, sticky="w"); self.perda_maxima_label = ttk.Label(parent_frame, text="$ 0.00", font=("-size 12 -weight bold"), bootstyle="danger"); self.perda_maxima_label.grid(row=1, column=8, padx=10, pady=2, sticky="w")
        ttk.Label(parent_frame, text="Posição Máxima:", font=("-size 10")).grid(row=0, column=9, padx=10, pady=2, sticky="w"); self.posicao_maxima_label = ttk.Label(parent_frame, text="0", font=("-size 12 -weight bold"), bootstyle="success"); self.posicao_maxima_label.grid(row=1, column=9, padx=10, pady=2, sticky="w")

    def _criar_filtros(self, parent_frame):
        # ... (código existente)
        ttk.Label(parent_frame, text="Filtrar por Ativo:").grid(row=0, column=0, padx=(0, 5), sticky="w")
        self.filtro_ativo_entry = ttk.Entry(parent_frame)
        self.filtro_ativo_entry.grid(row=1, column=0, padx=(0, 5), sticky="ew")
        ttk.Label(parent_frame, text="Data Início:").grid(row=0, column=1, padx=5, sticky="w")
        self.filtro_data_inicio = DateEntry(parent_frame, dateformat="%Y-%m-%d")
        self.filtro_data_inicio.grid(row=1, column=1, padx=5, sticky="ew")
        self.filtro_data_inicio.entry.delete(0, END)
        ttk.Label(parent_frame, text="Data Fim:").grid(row=0, column=2, padx=5, sticky="w")
        self.filtro_data_fim = DateEntry(parent_frame, dateformat="%Y-%m-%d")
        self.filtro_data_fim.grid(row=1, column=2, padx=5, sticky="ew")
        self.filtro_data_fim.entry.delete(0, END)
        filtrar_btn = ttk.Button(parent_frame, text="Filtrar", command=self._aplicar_filtro, bootstyle="info")
        filtrar_btn.grid(row=1, column=3, padx=5, sticky="ew")
        limpar_btn = ttk.Button(parent_frame, text="Limpar", command=self._limpar_filtro, bootstyle="secondary")
        limpar_btn.grid(row=1, column=4, padx=5, sticky="ew")
        self.edit_btn = ttk.Button(parent_frame, text="Editar", command=self._carregar_trade_para_edicao, bootstyle="outline-primary", state="disabled")
        self.edit_btn.grid(row=1, column=5, padx=5, sticky="ew")
        self.delete_btn = ttk.Button(parent_frame, text="Deletar", command=self._deletar_trade_selecionado, bootstyle="danger", state="disabled")
        self.delete_btn.grid(row=1, column=6, padx=5, sticky="ew")

    def _criar_formulario_entrada(self, parent_frame):
        # ... (código existente)
        self.entries = {}
        fields = {"Data:": {"key": "data"},"Horário:": {"key": "horario"},"Ativo:": {"key": "ativo"}, "Tipo (Compra/Venda):": {"key": "tipo_operacao"}, "Resultado:": {"key": "resultado_tipo"},"Valor Financeiro ($):": {"key": "resultado_financeiro"}}
        i=0
        for label_text, config in fields.items():
            ttk.Label(parent_frame, text=label_text).grid(row=0, column=i, sticky=W, padx=5)
            key = config["key"]
            if key == "resultado_tipo":
                widget = ttk.Combobox(parent_frame, values=["Gain", "Loss"], width=10, state="readonly")
                widget.current(0)
            else:
                widget = ttk.Entry(parent_frame, width=15)
            self.entries[key] = widget
            widget.grid(row=1, column=i, sticky=EW, padx=5)
            i += 1
        self.save_button = ttk.Button(parent_frame, text="Salvar", command=self._salvar_trade, bootstyle="primary")
        self.save_button.grid(row=0, column=i, rowspan=2, sticky="ns", padx=10)
        self.entries['data'].insert(0, date.today().strftime('%Y-%m-%d'))
        self.entries['horario'].insert(0, datetime.now().strftime('%H-%M-%S'))

    def _criar_tabela(self, parent_frame):
        # ... (código existente)
        colunas = ('id', 'data', 'horario', 'ativo', 'tipo_operacao', 'resultado_tipo', 'resultado_financeiro')
        self.tree = ttk.Treeview(parent_frame, columns=colunas, show='headings', bootstyle="primary")
        self.tree.configure(displaycolumns=('data', 'horario', 'ativo', 'tipo_operacao', 'resultado_tipo', 'resultado_financeiro'))
        headings_texts = ['ID', 'Data', 'Horário', 'Ativo', 'Tipo', 'Resultado', 'Valor ($)']
        column_widths = [40, 100, 80, 100, 100, 80, 100]
        for i, col in enumerate(colunas):
            self.tree.heading(col, text=headings_texts[i])
            self.tree.column(col, width=column_widths[i], anchor=CENTER)
        scrollbar = ttk.Scrollbar(parent_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        self.tree.bind('<ButtonRelease-1>', self._on_trade_select)

    def _criar_grafico(self, parent_frame):
        # ... (código existente)
        fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = fig.add_subplot(1, 1, 1)
        self.canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

    # --- Funções de Lógica e Eventos ---
    def atualizar_dados(self, filtro_ativo=None, data_inicio=None, data_fim=None):
        trades = data_manager.carregar_trades(filtro_ativo=filtro_ativo, data_inicio=data_inicio, data_fim=data_fim)
        self._popular_tabela(trades)
        self._atualizar_dashboard(trades)
        self._atualizar_grafico(trades)

    def _salvar_trade(self):
        trade_data = {}
        for key, widget in self.entries.items():
            trade_data[key] = widget.get()
        if trade_data.get('ativo'):
            trade_data['ativo'] = trade_data['ativo'].upper().strip()
        if not trade_data.get('ativo') or not trade_data.get('resultado_financeiro'):
            messagebox.showerror("Erro de Validação", "Os campos 'Ativo' e 'Valor Financeiro' são obrigatórios.")
            return
        try:
            if self.id_em_edicao is not None:
                data_manager.atualizar_trade(self.id_em_edicao, trade_data)
                messagebox.showinfo("Sucesso", "Operação atualizada com sucesso!")
            else:
                data_manager.salvar_trade(trade_data)
                messagebox.showinfo("Sucesso", "Operação salva com sucesso!")
            self._limpar_campos()
            self.atualizar_dados(filtro_ativo=self.filtro_ativo_entry.get(), data_inicio=self.filtro_data_inicio.entry.get(), data_fim=self.filtro_data_fim.entry.get())
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro inesperado:\n{e}")

    def _carregar_trade_para_edicao(self):
        selected_item = self.tree.focus()
        if not selected_item: return
        trade_values = self.tree.item(selected_item, 'values')
        self.id_em_edicao = trade_values[0]
        campos = ['data', 'horario', 'ativo', 'tipo_operacao', 'resultado_tipo', 'resultado_financeiro']
        for i, campo in enumerate(campos):
            widget = self.entries[campo]
            valor = trade_values[i + 1]
            if isinstance(widget, ttk.Combobox):
                widget.set(valor)
            else: # ttk.Entry
                widget.delete(0, END)
                widget.insert(0, valor)
        self.save_button.config(text="Atualizar")

    def _deletar_trade_selecionado(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Nenhuma seleção", "Por favor, selecione um trade na tabela para deletar.")
            return
        trade_values = self.tree.item(selected_item, 'values')
        trade_id = trade_values[0]
        resposta = messagebox.askyesno("Confirmar Deleção", f"Você tem certeza que deseja deletar o trade ID {trade_id} permanentemente?")
        if resposta:
            data_manager.deletar_trade(trade_id)
            self.atualizar_dados(filtro_ativo=self.filtro_ativo_entry.get(), data_inicio=self.filtro_data_inicio.entry.get(), data_fim=self.filtro_data_fim.entry.get())

    def _on_trade_select(self, event):
        if self.tree.focus():
            self.delete_btn.config(state="normal")
            self.edit_btn.config(state="normal")
        else:
            self.delete_btn.config(state="disabled")
            self.edit_btn.config(state="disabled")

    def _popular_tabela(self, trades):
        self.delete_btn.config(state="disabled")
        self.edit_btn.config(state="disabled")
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, trade in enumerate(trades):
            valores = [trade.get(col, '') for col in self.tree['columns']]
            tag = 'oddrow' if i % 2 == 0 else 'evenrow'
            self.tree.insert('', END, values=valores, tags=(tag,))
        self.tree.tag_configure('oddrow', background=None)
        self.tree.tag_configure('evenrow', background='#f0f0f0')

    def _limpar_campos(self):
        keys_to_clear = ['ativo', 'tipo_operacao', 'resultado_financeiro']
        for key in keys_to_clear:
            self.entries[key].delete(0, END)
        self.entries['horario'].delete(0, END)
        self.entries['horario'].insert(0, datetime.now().strftime('%H-%M-%S'))
        self.entries['resultado_tipo'].current(0)
        self.id_em_edicao = None
        self.save_button.config(text="Salvar")

    def _aplicar_filtro(self):
        filtro_ativo = self.filtro_ativo_entry.get().strip()
        data_inicio = self.filtro_data_inicio.entry.get()
        data_fim = self.filtro_data_fim.entry.get()
        self.atualizar_dados(filtro_ativo=filtro_ativo if filtro_ativo else None, data_inicio=data_inicio if data_inicio else None, data_fim=data_fim if data_fim else None)

    def _limpar_filtro(self):
        self.filtro_ativo_entry.delete(0, END)
        self.filtro_data_inicio.entry.delete(0, END)
        self.filtro_data_fim.entry.delete(0, END)
        self.atualizar_dados()
    
    def _calcular_risco(self):
        
        try:
            self.perda_maxima_label.config(text="$ 0.00")
            self.posicao_maxima_label.config(text="0")

            # --- Parte 1: Cálculo da Perda Máxima ---
            # MUDANÇA: Adicionado .replace(',', '.') para aceitar vírgula como decimal
            patrimonio = float(self.patrimonio_entry.get().replace(',', '.'))
            risco_percent = float(self.risco_percent_entry.get().replace(',', '.'))

            perda_maxima = (patrimonio * risco_percent) / 100.0
            self.perda_maxima_label.config(text=f"$ {perda_maxima:.2f}")

            # --- Parte 2: Cálculo do Tamanho da Posição ---
            # MUDANÇA: Adicionado .replace(',', '.') aqui também
            preco_entrada_str = self.entrada_entry.get().replace(',', '.')
            preco_stop_str = self.stop_entry.get().replace(',', '.')
            valor_ponto_str = self.valor_ponto_entry.get().replace(',', '.')

            if preco_entrada_str and preco_stop_str and valor_ponto_str:
                preco_entrada = float(preco_entrada_str)
                preco_stop = float(preco_stop_str)
                valor_ponto = float(valor_ponto_str)

                distancia_stop_pontos = abs(preco_entrada - preco_stop)
                risco_financeiro_unitario = distancia_stop_pontos * valor_ponto

                if risco_financeiro_unitario > 0:
                    posicao_maxima = math.floor(perda_maxima / risco_financeiro_unitario)
                    self.posicao_maxima_label.config(text=f"{posicao_maxima} contratos")
                else:
                    self.posicao_maxima_label.config(text="Verifique os preços")

        except (ValueError, TypeError):
            self.perda_maxima_label.config(text="Entrada inválida")
            self.posicao_maxima_label.config(text="---")

    def _on_asset_select(self, event):
        ativo_selecionado = self.ativo_calculadora_combo.get()
        valor_do_ponto = VALORES_POR_PONTO.get(ativo_selecionado, 0.0)
        self.valor_ponto_entry.config(state="normal")
        self.valor_ponto_entry.delete(0, END)
        self.valor_ponto_entry.insert(0, str(valor_do_ponto))
        self.valor_ponto_entry.config(state="readonly")
        self._calcular_risco()

    def _preencher_patrimonio_com_saldo(self):
        if hasattr(self, 'saldo_atual'):
            self.patrimonio_entry.delete(0, END)
            self.patrimonio_entry.insert(0, f"{self.saldo_atual:.2f}")
            self._calcular_risco()
        else:
            messagebox.showwarning("Aviso", "O saldo ainda não foi calculado. Adicione um trade primeiro.")
    
    def _atualizar_grafico(self, trades):
        eixo_x, eixo_y = analytics.preparar_dados_grafico(trades)
        self.ax.clear()
        self.ax.plot(eixo_x, eixo_y, marker='o', linestyle='-')
        self.ax.axhline(0, color='grey', linestyle='--')
        self.ax.set_title("Curva de Patrimônio (Equity Curve)")
        self.ax.set_xlabel("Número da Operação")
        self.ax.set_ylabel("Patrimônio Acumulado ($)")
        self.ax.grid(True)
        self.canvas.draw()
    
    # Adicione esta função completa dentro da sua classe TradingJournalApp

    def _atualizar_dashboard(self, trades):
        metricas = analytics.calcular_metricas(trades)
        saldo_usd = metricas['saldo_total']
        self.saldo_atual = saldo_usd # Guarda o saldo para a calculadora

        # Atualiza o saldo em USD
        saldo_style = "success" if saldo_usd >= 0 else "danger"
        self.saldo_label.config(text=f"$ {saldo_usd:.2f}", bootstyle=saldo_style)

        # Atualiza as outras métricas
        self.total_ops_label.config(text=f"{metricas['total_operacoes']}")
        self.taxa_acerto_label.config(text=f"{metricas['taxa_acerto']:.2f}%")

        # Lógica para o Payoff
        payoff = metricas['payoff_ratio']
        payoff_style = "success" if payoff >= 1.5 else "warning" if payoff >= 1.0 else "danger"
        self.payoff_label.config(text=f"{payoff:.2f}", bootstyle=payoff_style)

        # Lógica para BRL
        taxa_cambio = api_service.obter_taxa_cambio_usd_brl()
        if taxa_cambio is not None:
            saldo_brl = saldo_usd * taxa_cambio
            self.saldo_brl_label.config(text=f"R$ {saldo_brl:.2f}")
        else:
            self.saldo_brl_label.config(text="Cotação N/A", bootstyle="warning")

def main():
    data_manager.inicializar_banco()
    root = ttk.Window(themename="litera")
    app = TradingJournalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()