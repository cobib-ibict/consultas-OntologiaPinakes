# Importação das bibliotecas necessárias
import pandas as pd  # Para manipulação de planilhas Excel
import os  # Para operações com sistema de arquivos
import re  # Para operações com expressões regulares
from pathlib import Path  # Para manipulação de caminhos de arquivos

def limpar_consulta(consulta):
    """Remove linhas de comentário e espaços desnecessários da consulta SPARQL"""
    if pd.isna(consulta):  # Verifica se o valor é vazio/NaN
        return ""
    
    linhas = []
    for linha in consulta.split('\n'):  # Divide a consulta por linhas
        linha = linha.strip()  # Remove espaços em branco no início e fim
        # Mantém apenas linhas não vazias e que não são comentários
        if linha and not linha.startswith(('#', '//')):
            linhas.append(linha)
    
    return '\n'.join(linhas)  # Junta as linhas válidas novamente

def processar_respostas(respostas):
    """Processa as respostas esperadas, normalizando seu formato"""
    if pd.isna(respostas):  # Verifica se o valor é vazio/NaN
        return ""
    
    respostas_str = str(respostas)  # Converte para string
    # Divide as respostas por ponto-e-vírgula, ignorando os dentro de aspas
    partes = re.split(r';(?=(?:[^"]*"[^"]*")*[^"]*$)', respostas_str)
    
    linhas_respostas = []
    for resposta in partes:
        resposta = resposta.strip().strip('"')  # Remove espaços e aspas extras
        if not resposta:  # Ignora strings vazias
            continue
        
        # Remove anotações de idioma (@pt-BR) e tipos de dados (^^xsd:)
        resposta = re.sub(r'@\S+|\^\^xsd:\w+', '', resposta).strip()
        
        # Remove prefixo 'ex:' se presente
        if resposta.startswith('ex:'):
            resposta = resposta[3:]
        # Extrai apenas a última parte de URIs
        elif resposta.startswith('http'):
            resposta = resposta.split('/')[-1].split('#')[-1]
        
        # Formata como comentário no arquivo .rq
        linhas_respostas.append(f"# Resposta esperada: {resposta}")
    
    return '\n'.join(linhas_respostas)  # Retorna todas as respostas formatadas

def extrair_variavel_principal(consulta):
    """Extrai a primeira variável após o SELECT na consulta SPARQL"""
    # Busca padrão SELECT seguido de variáveis (?var) até WHERE
    match = re.search(r'SELECT\s+(?:\?(\w+)\s*)+WHERE', consulta, re.IGNORECASE)
    return match.group(1) if match else None  # Retorna a primeira variável encontrada

def gerar_arquivos_rq():
    """Gera arquivos .rq com consultas SPARQL a partir da planilha"""
    # Configura caminhos dos arquivos
    script_dir = Path(__file__).parent  # Diretório do script
    planilha_path = script_dir.parent / "ConsultaSPARQLdasQCs.xlsx"  # Planilha de entrada
    pasta_saida = script_dir.parent / "competencias"  # Pasta de saída
    
    # Lê a planilha Excel
    df = pd.read_excel(planilha_path, sheet_name="Página2")
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Processa cada linha da planilha
    for _, row in df.iterrows():
        if pd.isna(row["Consulta SPARQL"]):  # Ignora linhas sem consulta
            continue
        
        # Extrai número da questão (ex: "QC1" de "QC1-Qual é o título...")
        qc_num = row["Questao de Competência"].split('-')[0].strip()
        # Processa respostas e consulta
        respostas = processar_respostas(row["Respostas"])
        consulta = limpar_consulta(row["Consulta SPARQL"])
        
        # Obtém variável principal ou usa "resultado" como padrão
        var_principal = extrair_variavel_principal(consulta) or "resultado"
        # Simplifica consulta para retornar apenas a variável principal
        consulta = re.sub(r'SELECT\s+.+?\s+WHERE', 
                        f'SELECT ?{var_principal} WHERE', 
                        consulta, 
                        flags=re.IGNORECASE)
        
        # Monta o conteúdo do arquivo .rq
        partes = [
            f"# {row['Questao de Competência']}",  # Título como comentário
            respostas,  # Respostas esperadas como comentários
            # Prefixos SPARQL padrão
            "PREFIX ex: <http://www.semanticweb.org/kely/ontologies/2023/11/pinakes#>",
            "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>",
            "",  # Linha vazia para separação
            consulta  # Consulta SPARQL propriamente dita
        ]
        
        # Junta todas as partes do arquivo
        conteudo = '\n'.join(partes)
        # Escreve o arquivo .rq na pasta de saída
        with open(pasta_saida / f"{qc_num}.rq", "w", encoding='utf-8') as f:
            f.write(conteudo)
    
    # Mensagem de confirmação
    print(f"✅ Arquivos .rq gerados corretamente em: {pasta_saida}")

if __name__ == "__main__":
    # Executa a função principal quando o script é chamado diretamente
    gerar_arquivos_rq()