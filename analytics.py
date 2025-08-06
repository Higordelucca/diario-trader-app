# analytics.py

def calcular_metricas(trades):
    if not trades:
        return {
            'saldo_total': 0.0,
            'total_operacoes': 0,
            'taxa_acerto': 0.0
        }

    saldo_total = 0.0
    operacoes_vencedoras = 0
    total_operacoes = len(trades)

    for trade in trades:
        # Acumula o saldo financeiro
        try:
            resultado_financeiro = float(trade.get('resultado_financeiro', 0))
            if trade.get('resultado_tipo') == 'Loss':
                saldo_total -= resultado_financeiro
            else:
                saldo_total += resultado_financeiro

        except (ValueError, TypeError):
            print(f"Aviso: Valor inválido encontrado em um trade: {trade.get('resultado_financeiro')}")
            continue
        
        if trade.get('resultado_tipo') == 'Gain':
            operacoes_vencedoras += 1

    # Calcula a taxa de acerto, evitando divisão por zero
    taxa_acerto = (operacoes_vencedoras / total_operacoes) * 100 if total_operacoes > 0 else 0

    return {
        'saldo_total': saldo_total,
        'total_operacoes': total_operacoes,
        'taxa_acerto': taxa_acerto
    }