# 🤖 Doc Intelligence RAG (M.O.T.H.E.R. Interface)

Este repositório contém o código de uma IA especializada em análise de documentos técnicos utilizando a arquitetura **RAG (Retrieval-Augmented Generation)**. O projeto, apelidado de **M.O.T.H.E.R.**, permite que usuários subam manuais em PDF e consultem informações complexas através de linguagem natural com alta precisão e persistência de dados.



## 🚀 Funcionalidades Principais

* **Persistência de Memória**: Utiliza um sistema de arquivos de configuração (`config_memoria.txt`) para garantir que o último manual carregado seja lembrado mesmo após o servidor ser reiniciado.
* **Isolamento Dinâmico**: Cada novo documento processado cria uma "célula de memória" única (subpastas com timestamp), evitando a sobreposição ou mistura de informações de manuais diferentes.
* **Interface Inteligente**: Desenvolvido em Streamlit, oferece um modo de edição completo para mudar instruções ou limpar a memória física do banco de dados.
* **Auditabilidade (Debug Mode)**: Inclui um relatório de inteligência que exibe exatamente quais trechos do PDF foram recuperados para gerar a resposta da IA.
* **Geração de Documentos**: Integração com a biblioteca `fpdf2` para criação de novos relatórios ou documentos a partir das interações.

## 🛠️ Tecnologias Utilizadas

* **Python 3.12**
* **Streamlit**: Interface do usuário e frontend.
* **LangChain**: Orquestração do pipeline RAG.
* **ChromaDB**: Banco de dados vetorial para armazenamento persistente.
* **Groq API (Llama 3.1)**: Motor de inferência de alto desempenho.
* **HuggingFace Embeddings**: Transformação de texto em vetores semânticos.

## 📂 Estrutura do Projeto

```text
.
├── app_streamlit.py       # Código principal da aplicação
├── requirements.txt       # Dependências do projeto
├── .env                  # Variáveis de ambiente (API Keys)
├── .gitignore            # Arquivos ignorados pelo Git
├── memorias/             # Pasta onde os bancos de dados são salvos
└── config_memoria.txt    # Arquivo que persiste o caminho do último manual
