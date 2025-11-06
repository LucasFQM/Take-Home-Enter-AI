# 📋 Take Home Enter AI - PDF Extractor API

## 🎯 Objetivo

O objetivo foi tentar extrair informações estruturadas de arquivos PDFs de forma síncrona e com o melhor custo-benefício e a maior acurácia possível. Ou seja, a proposta solicitou que cada requisição fosse respondida em menos de 10 segundos e que pelo menos 80% dos campos fossem extraídos corretamente.

## 🤖 Metodologia

### Extração

Os principais desafios da proposta, sem dúvidas, foram:

- A variação nas estruturas e formatações dos PDFs, o que dificultou a extração consistente das informações.

- A existência de diferentes tipos de PDFs, cada um contendo campos distintos.

Para contornar esses desafios, foi implementada uma função genérica (utilizando a biblioteca PyMuPDF) denominada `extract_text_from_pdf_bytes()`, que recebe os bytes de um arquivo PDF e retorna o texto extraído. Ou seja, o objetivo foi permitir que o mesmo código pudesse ser reutilizado para múltiplos tipos de documentos.

### Processamento

Foi solicitado o processamento de múltiplos arquivos de forma sequencial (em série), isto é, garantindo que cada arquivo fosse tratado de maneira independente.
Dessa forma, optou-se por implementar a classe `PDFExtractorClient`, responsável por processar todos os PDFs de uma pasta, enviando-os um a um para a API.

### Armazenamento

A partir das execuções, foi gerado um arquivo denominado `relatorio_extracao.json`, utilizado para armazenar todas as informações extraídas em formato estruturado.
Por fim, foi mantida uma base incremental em `knowledge_base.json`.

## 📁 Estrutura do Projeto

```text
TAKE_HOME_ENTER_AI/
│
├── src/ # Pasta onde os PDFs devem ser colocados
│ ├── main.py # API FastAPI (endpoint /extract)
│ ├── utils/
│ │ ├── init.py
│ │ └── pdf_utils.py # Funções de extração de texto e campos
│ ├── test_extract.py # Cliente para processar PDFs em lote
│ ├── relatorio_extracao.json # Relatório de saída gerado após o teste
│ ├── knowledge_base.json # Base incremental de conhecimento
│ ├── *.pdf # PDFs de exemplo (OAB e Telas de Sistema)
│ └── requirements.txt # Dependências do projeto
│
└── README.md # Documentação do projeto
```

## 🚀 Como Começar

### 1. Instalar dependências

No diretório raiz do projeto, execute:

```pip install -r requirements.txt```

### 2. Executar a API

Dentro da pasta ```src```, inicie o servidor FastAPI com:

```uvicorn main:app --reload```

### 3. Executar o processamento

Em outro terminal, execute o cliente:

```python test_extract.py```



## 👨‍💻 Autor

Lucas Ferreira Quintão Moreira. O desenvolvimento desta proposta contou com o auxílio de LLMs, consultas a documentações e outras referências.