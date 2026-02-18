# 🤖 Doc Intelligence RAG (M.O.T.H.E.R. Interface)

Este projeto consiste em um sistema avançado de **RAG (Retrieval-Augmented Generation)** projetado para transformar documentos PDF em bases de conhecimento consultáveis. Apelidado de **M.O.T.H.E.R.**, o sistema utiliza inteligência artificial para responder perguntas técnicas com precisão, mantendo a imersão em uma interface temática de base lunar.



## 🛠️ Arquitetura do Sistema

O projeto foi estruturado para superar as limitações de bloqueio de arquivos em sistemas Windows, utilizando um método de **Compartimentação Dinâmica de Memória**:

* **Persistência de Longo Prazo**: O arquivo `config_memoria.txt` armazena o caminho da última célula de memória ativa, garantindo que o manual não seja esquecido após reiniciar o sistema.
* **Isolamento de Dados**: Cada novo manual processado cria uma subpasta única dentro de `./memorias/`, evitando a mistura de contextos entre diferentes documentos.
* **Performance**: Utiliza `@st.cache_resource` para carregamento instantâneo dos modelos de Embedding após a primeira inicialização.

## 📂 Estrutura de Arquivos

Conforme visualizado no ambiente de desenvolvimento:

```text
.
├── app_streamlit.py       # Interface principal e lógica do chatbot
├── requirements.txt       # Dependências do projeto (fpdf2, langchain, etc.)
├── .env                  # Chaves de API (não incluídas no repositório)
├── .gitignore            # Proteção contra upload de dados sensíveis e cache
├── config_memoria.txt    # Persistência do caminho do banco ativo
├── memorias/             # Diretório de armazenamento dos bancos vetoriais
│   └── banco_177144...   # Células de memória isoladas por timestamp
├── manuais/              # PDFs originais para processamento
└── gerador_pdf/          # Scripts auxiliares para criação de documentos
```

Desenvolvido por Heitor - Doc Intelligence RAG
