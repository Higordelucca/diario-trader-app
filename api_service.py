import requests

def obter_taxa_cambio_usd_brl():
    url = "https://open.er-api.com/v6/latest/USD"
    
    try:
        # Faz uma requisição para a url com timeout 5 segundos
        response = requests.get(url, timeout=5)
        
        # Verifica se a requisição foi bem sucedida (200)
        if response.status_code == 200:
            data = response.json()
            # pega a catação
            taxa_brl = data.get('rates', {}).get('BRL')
            if taxa_brl:
                return float(taxa_brl)
        else:
            print(f"Erro ao buscar dados da API: Status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # Captura erro de coneção, timeout, etc
        print(f"Erro de coneção com a API de câmbio: {e}")
        return None