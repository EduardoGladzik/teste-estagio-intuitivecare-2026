import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/"

def get_links(url):
    '''Retorna lista dos links válidos encontrados na URL.'''
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        valid_links = []
        for node in soup.find_all('a'):
            href = node.get('href')
            text = node.get_text().strip()
            
            # Evita links inválidos ou que o script retorne a pasta raiz ou que subam níveis
            if not href or href.startswith('?') or "Parent Directory" in text or ".." in href:
                continue
                
            full_url = urljoin(url, href)
            
            # Garante que o link é realmente uma subpasta
            if full_url.startswith(url) and full_url != url:
                valid_links.append((text, full_url))
        
        return valid_links
    except Exception as e:
        print(f"Erro ao buscar links {url}: {e}")
        return []

def search_for_quarters(base_url, quantity=3):
    print(f"Iniciando busca em: {base_url}")
    
    # finds 'demonstracoes_contabeis'
    root_links = get_links(base_url)
    financial_statements_url = next((url for txt, url in root_links if "demonstracoes_contabeis" in txt.lower() or "demonstracoes_contabeis" in url), None)
    
    if not financial_statements_url:
        print("Pasta 'demonstracoes_contabeis' não encontrada.")
        return []

    # finds year folders
    year_links = get_links(financial_statements_url)
    yers = sorted([url for txt, url in year_links if txt.strip('/').isdigit()], reverse=True)
    
    complete_links = []
    
    # finds quarters
    for year_url in yers:
        year_str = year_url.rstrip('/').split('/')[-1]
        print(f"Verificando ano: {year_str}")
        
        links_subs = get_links(year_url)
        # filters links that suggest quarters
        quarters = sorted([url for txt, url in links_subs if 'T' in txt.upper()], reverse=True)
        
        for quarter in quarters:
            if len(complete_links) < quantity:
                complete_links.append(quarter)
            else:
                break
        
        if len(complete_links) >= quantity:
            break
            
    return complete_links

print("\n--- Arquivos encontrados ---")
for link in search_for_quarters(BASE_URL):
    print(link)