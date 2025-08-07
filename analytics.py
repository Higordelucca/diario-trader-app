# analytics.py

def calcular_metricas(trades):
    """
    Calcula as métricas de performance a partir de uma lista de trades.
    """
    if not trades:
        return {
            'saldo_total': 0.0,
            'total_operacoes': 0,
            'taxa_acerto': 0.0,
            'payoff_ratio': 0.0 # Adiciona o novo campo
        }

    saldo_total = 0.0
    operacoes_vencedoras = 0
    total_operacoes = len(trades)

    # Novas variáveis para o cálculo do Payoff
    total_ganho = 0.0
    total_perda = 0.0
    operacoes_perdedoras = 0

    for trade in trades:
        try:
            resultado_financeiro = float(trade.get('resultado_financeiro', 0))

            if trade.get('resultado_tipo') == 'Loss':
                saldo_total -= resultado_financeiro
                # Acumula valores para o Payoff
                total_perda += resultado_financeiro
                operacoes_perdedoras += 1
            else: # 'Gain'
                saldo_total += resultado_financeiro
                # Acumula valores para o Payoff
                total_ganho += resultado_financeiro
                operacoes_vencedoras += 1

        except (ValueError, TypeError):
            continue

    # --- Lógica de Cálculo Final ---
    taxa_acerto = (operacoes_vencedoras / total_operacoes) * 100 if total_operacoes > 0 else 0

    # Cálculo do Payoff
    ganho_medio = total_ganho / operacoes_vencedoras if operacoes_vencedoras > 0 else 0
    perda_media = total_perda / operacoes_perdedoras if operacoes_perdedoras > 0 else 0

    payoff_ratio = ganho_medio / abs(perda_media) if perda_media != 0 else 0

    return {
        'saldo_total': saldo_total,
        'total_operacoes': total_operacoes,
        'taxa_acerto': taxa_acerto,
        'payoff_ratio': payoff_ratio # Retorna a nova métrica
    }

def preparar_dados_grafico(trades):
    """
    Prepara os dados para a plotagem do gráfico da curva de patrimônio.
    """
    eixo_x = [0]
    eixo_y = [0.0]
    
    patrimonio_acumulado = 0.0
    
    trades_ordenados = sorted(trades, key=lambda t: int(t['id']))

    for i, trade in enumerate(trades_ordenados, 1):
        try:
            resultado_financeiro = float(trade.get('resultado_financeiro', 0))
            
            if trade.get('resultado_tipo') == 'Loss':
                patrimonio_acumulado -= resultado_financeiro
            else:
                patrimonio_acumulado += resultado_financeiro
            
            eixo_x.append(i)
            eixo_y.append(patrimonio_acumulado)

        except (ValueError, TypeError):
            continue

    return eixo_x, eixo_y
