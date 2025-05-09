# 📚 Consultas SPARQL para a Ontologia Pinakes

Repositório contendo **59 consultas SPARQL** mapeadas para as **competências da Ontologia Pinakes**, geradas automaticamente a partir da planilha `ConsultaSPARQLdasQCs.xlsx`.

## 🗂️ Estrutura do Repositório
/consultas-OntologiaPinakes/
├── 📁 competencias/ # Consultas individuais (QC1-QC59)
│ ├── QC1.rq # Exemplo: Consulta para título da obra
│ └── ... # Demais consultas
├── 📁 scripts/
│ ├── planilha_para_sparql.py # Script de geração das consultas
│ └── validador_sparql.py # Validador de consultas (opcional)
├── 📄 pinakesfull.rdf # Ontologia completa
├── 📄 ConsultaSPARQLdasQCs.xlsx # Planilha de origem
└── 📄 README.md # Este arquivo
└── 📄 relatorio_completo_pinakes # relatório de validação das QCs gerado pelo validador_sparql.py

## 🔍 Prefixos da Ontologia

Os prefixos abaixo foram extraídos diretamente do arquivo `pinakesfull.rdf`:

```sparql
PREFIX ex: <http://www.semanticweb.org/kely/ontologies/2023/11/pinakes#>  
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

🔧 Pré-requisitos:
  1. Python 3.x (para executar os scripts)
  2. Editor SPARQL (Protégé, Jena Fuseki ou online)


🚀 Como Usar
1. Executando Consultas
  1.Carregue o arquivo RDF em um endpoint SPARQL: 

Ferramentas online: SPARQL Playground, Graph DB

Localmente: Apache Jena Fuseki

  2.Copie uma consulta da pasta competencias/ e execute no endpoint.


2. Validando Consultas (opcional, usando Graph DB)
Para validar todas as consultas contra o arquivo RDF:
```bash
  python scripts/validador_graphdb.py  

📊 Exemplo de Consulta SPARQL (QC1.rq)

# QC1: Qual é o título de uma determinada obra?

PREFIX ex: <http://www.semanticweb.org/kely/ontologies/2023/11/pinakes#>  
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?tituloProprio 
WHERE {
  ?obra a pinakes:Obra ;  
        pinakes:tituloProprio ?tituloProprio . 
  #FILTER EXISTS {  
  #  ?obra a pinakes:PublicacaoSeriada .  
  #} 
    #FILTER(CONTAINS(LCASE(?tituloProprio), "ciência"))  
}

🛠️ Como Contribuir
 1. **Atualize** a planilha **ConsultaSPARQLdasQCs.xlsx** quando necessário

 2. Regenere as consultas executando:
python scripts/planilha_para_sparql.py

 3. Documente mudanças no histórico abaixo
📌 Histórico de Atualizações 
**Data**      	**Versão**	   **Mudanças**
26-03-2025	   1.0	      Versão inicial das consultas
07-05-2025         1.7        Versão atual

❓ Dúvidas Frequentes
Q: Como adicionar novas consultas?
R: Basta incluir na planilha e executar o script novamente.

Q: Os prefixos estão incorretos para minha versão da ontologia?
R: Atualize-os no script planilha_para_sparql.py e gere os arquivos novamente.

Q: Arquivo RDF não carrega?
R: Verifique a sintaxe do RDF.

Q: O que fazer se resultados forem diferente do esperado ou aparecer erros no relatório gerado?
R: Verifique se os arquivos rq foram extraidos corretamente e ajustá-los. Verificação individual de cada consulta no Graph DB usando os Select da Planilha e os prefixos da Ontologia. Atualizar os arquivos no mesmo diretório. Verificar RDF da Ontologia: estrutura e existencia de Instâncias. Persistindo o problema, entrar em contato para reportá-lo.

✉️ Contato: greicysantos@ibict.br

ℹ️ Nota: Todas as consultas foram validadas contra o arquivo pinakesfull.rdf importado para o repositório pinakes criado no Graph DB. O relatório gerado está validando cerca de 94% das questões. Os arquivos das questões 56, 57 e 58 estão sendo gerados com erro no script implicando em resultados obtidos diferente dos esperados e por isso foram ajustadas manualmente, para gerar o relatório que está disponível nesse repositório. Recomenda-se a verificação dos arquivos .rq sempre que os resultados derem erros o diferente do esperado.
