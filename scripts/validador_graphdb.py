# Importação das bibliotecas necessárias
import pandas as pd  # Para manipulação de dados em planilhas
import os  # Para operações com sistema de arquivos
import glob  # Para encontrar arquivos usando padrões
import re  # Para operações com expressões regulares
from SPARQLWrapper import SPARQLWrapper, JSON  # Para consultas SPARQL
from pathlib import Path  # Para manipulação de caminhos de arquivos

# Endpoint do GraphDB onde as consultas serão executadas
GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/pinakes" #substitua pelo caminho do seu repositório no Graph DB

def normalizar_resposta(resposta):
    """Normaliza uma resposta removendo formatações desnecessárias"""
    if pd.isna(resposta):  # Verifica se o valor é NaN
        return ""
    resposta = str(resposta).strip()  # Converte para string e remove espaços extras
    # Remove anotações de idioma (@pt-BR), tipos de dados (^^xsd:) e aspas
    resposta = re.sub(r'@\S+|\^\^xsd:\w+|"', '', resposta)

    # Remove prefixo 'ex:' se presente
    if resposta.startswith('ex:'):
        resposta = resposta[3:]
    # Extrai apenas a última parte de URIs
    elif resposta.startswith('http'):
        resposta = resposta.split('/')[-1].split('#')[-1]

    return resposta.strip()  # Remove espaços extras novamente e retorna

def carregar_respostas():
    """Carrega as respostas esperadas da planilha Excel"""
    script_dir = Path(__file__).parent  # Obtém diretório do script
    planilha_path = script_dir.parent / "ConsultaSPARQLdasQCs.xlsx"  # Caminho da planilha 
    df = pd.read_excel(planilha_path, sheet_name="Página2")  # Lê a planilha
    respostas = {}  # Dicionário para armazenar as respostas

    for _, row in df.iterrows():  # Itera sobre cada linha do DataFrame
        if pd.notna(row["Respostas"]):  # Verifica se há resposta na linha
            # Extrai o número da questão (ex: "QC1" de "QC1-Qual é o título...")
            qc_num = row["Questao de Competência"].split('-')[0].strip()
            # Divide as respostas por ponto-e-vírgula, ignorando os dentro de aspas
            partes = re.split(r';(?=(?:[^"]*"[^"]*")*[^"]*$)', str(row["Respostas"]))
            # Normaliza cada resposta e armazena no dicionário
            respostas[qc_num] = [
                normalizar_resposta(r.strip()) 
                for r in partes
                if r.strip()  # Ignora strings vazias
            ]
    return respostas

def validar_consulta(arquivo_rq, respostas_esperadas):
    """Executa uma consulta SPARQL e valida os resultados"""
    try:
        # Lê o conteúdo do arquivo .rq
        with open(arquivo_rq, 'r', encoding='utf-8') as f:
            conteudo = ""
            in_query = False
            for linha in f:
                if linha.startswith("PREFIX"):  # Marca início da consulta
                    in_query = True
                if in_query:
                    conteudo += linha  # Acumula linhas da consulta

        # Extrai o número da questão do nome do arquivo
        qc_num = os.path.basename(arquivo_rq).split('.')[0]
        # Obtém respostas esperadas para esta questão
        respostas_esperadas = respostas_esperadas.get(qc_num, [])

        # Configura e executa a consulta SPARQL
        sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
        sparql.setQuery(conteudo)
        sparql.setReturnFormat(JSON)
        resultados = sparql.query().convert()  # Executa e converte para JSON

        # Extrai variáveis e resultados da consulta
        vars_resultado = resultados['head']['vars']
        dados = resultados['results']['bindings']

        valores_obtidos = set()  # Armazena valores únicos obtidos
        for item in dados:  # Para cada resultado da consulta
            for var in vars_resultado:  # Para cada variável no SELECT
                # Obtém e normaliza o valor da variável
                valor = normalizar_resposta(item.get(var, {}).get('value', ''))
                if valor:  # Se não for vazio, adiciona ao conjunto
                    valores_obtidos.add(valor)

        # Verifica se todas as respostas esperadas foram encontradas
        todas_encontradas = all(
            any(resposta_esperada == valor for valor in valores_obtidos)
            for resposta_esperada in respostas_esperadas
        ) if respostas_esperadas else True  # Se não há respostas esperadas, considera correto

        # Retorna dicionário com resultados da validação
        return {
            'status': '✅ CORRETO' if todas_encontradas else '⚠️ DIFERENTE',
            'esperado': '; '.join(respostas_esperadas),  # Respostas esperadas formatadas
            'obtido': '; '.join(valores_obtidos),  # Valores obtidos formatados
            'variaveis': vars_resultado  # Lista de variáveis retornadas
        }

    except Exception as e:  # Em caso de erro na consulta
        return {
            'status': f'❌ ERRO: {str(e)}',
            'esperado': '; '.join(respostas_esperadas) if respostas_esperadas else '',
            'obtido': '',
            'variaveis': []
        }

def gerar_relatorio():
    """Gera um relatório com os resultados de todas as validações"""
    script_dir = Path(__file__).parent  # Diretório do script
    # Caminhos para os arquivos de saída e consultas
    relatorio_path = script_dir.parent / "relatorio_validacao_avancado.txt"
    consultas_dir = script_dir.parent / "competencias"
    respostas = carregar_respostas()  # Carrega respostas esperadas

    with open(relatorio_path, 'w', encoding='utf-8') as relatorio:
        # Cabeçalho do relatório
        relatorio.write("RELATÓRIO DE VALIDAÇÃO AVANÇADO\n")
        relatorio.write("="*80 + "\n\n")

        total = corretas = diferentes = erros = 0  # Contadores

        # Para cada arquivo .rq no diretório de consultas
        for arquivo in sorted(glob.glob(str(consultas_dir / '*.rq'))):
            qc_num = os.path.basename(arquivo).split('.')[0]  # Número da questão
            resultado = validar_consulta(arquivo, respostas)  # Valida consulta

            # Escreve resultados no relatório
            relatorio.write(f"{qc_num}:\n")
            relatorio.write(f"Status: {resultado['status']}\n")

            if 'ERRO' in resultado['status']:
                erros += 1
                relatorio.write(f"Detalhes: {resultado['status']}\n")
            else:
                relatorio.write(f"Esperado: {resultado['esperado']}\n")
                relatorio.write(f"Obtido: {resultado['obtido']}\n")
                if 'CORRETO' in resultado['status']:
                    corretas += 1
                else:
                    diferentes += 1

            relatorio.write("-"*80 + "\n")  # Linha separadora
            total += 1

        # Resumo final
        relatorio.write("\nRESUMO FINAL:\n")
        relatorio.write(f"Total: {total} | Corretas: {corretas} | Diferentes: {diferentes} | Erros: {erros}\n")
        relatorio.write(f"Taxa de acerto: {corretas/total*100:.1f}%\n" if total > 0 else "Taxa de acerto: N/A\n")

if __name__ == "__main__":
    gerar_relatorio()  # Executa a geração do relatório quando o script é chamado diretamente


