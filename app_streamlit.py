import streamlit as st
import os
import shutil
import tempfile
import gc
import time
from dotenv import load_dotenv

# --- IMPORTAÇÕES ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq

load_dotenv()

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="M.O.T.H.E.R. - Gestão de Memória", page_icon="🧠")

PASTA_BASE = "./memorias"
ARQUIVO_CONFIG = "config_memoria.txt"

if not os.path.exists(PASTA_BASE):
    os.makedirs(PASTA_BASE)

# --- FUNÇÕES DE PERSISTÊNCIA ---
def salvar_ultimo_caminho(caminho):
    with open(ARQUIVO_CONFIG, "w") as f:
        f.write(caminho)

def ler_ultimo_caminho():
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, "r") as f:
            caminho = f.read().strip()
            if os.path.exists(caminho):
                return caminho
    return os.path.join(PASTA_BASE, "banco_vazio")

@st.cache_resource
def carregar_modelo_embedding():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

EMBEDDING_MODEL = carregar_modelo_embedding()

# --- ESTADOS DA SESSÃO ---
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "editando" not in st.session_state:
    st.session_state.editando = False

# Carrega o caminho do arquivo de texto ao iniciar
if "caminho_atual" not in st.session_state:
    st.session_state.caminho_atual = ler_ultimo_caminho()

# Carregamento inicial do Banco baseado no caminho persistido
if "vector_db" not in st.session_state:
    if os.path.exists(st.session_state.caminho_atual) and os.listdir(st.session_state.caminho_atual):
        st.session_state.vector_db = Chroma(
            persist_directory=st.session_state.caminho_atual, 
            embedding_function=EMBEDDING_MODEL
        )
    else:
        st.session_state.vector_db = None

# --- FUNÇÕES DE GERENCIAMENTO ---
def limpar_tudo_e_zerar():
    st.session_state.vector_db = None
    st.session_state.mensagens = []
    # Reseta o arquivo de configuração
    if os.path.exists(ARQUIVO_CONFIG):
        os.remove(ARQUIVO_CONFIG)
    st.session_state.caminho_atual = os.path.join(PASTA_BASE, "banco_vazio")
    gc.collect()
    st.session_state.editando = False
    st.rerun()

def processar_novo_pdf(uploaded_file):
    st.session_state.mensagens = []
    nova_pasta = os.path.join(PASTA_BASE, f"banco_{int(time.time())}")
    
    with st.spinner("Gravando nova célula de memória permanente..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            caminho_pdf = tmp.name
        
        loader = PyPDFLoader(caminho_pdf)
        splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(loader.load())
        
        st.session_state.vector_db = Chroma.from_documents(
            documents=splits, 
            embedding=EMBEDDING_MODEL,
            persist_directory=nova_pasta
        )
        
        # Salva o novo caminho no arquivo TXT para persistência total
        st.session_state.caminho_atual = nova_pasta
        salvar_ultimo_caminho(nova_pasta)
        
        os.remove(caminho_pdf)
        st.session_state.editando = False
        st.success("Memória sincronizada e salva no disco!")
        time.sleep(1)
        st.rerun()
# --- INTERFACE ---
st.title("🤖 M.O.T.H.E.R. - Interface Neural")

with st.sidebar:
    st.header("⚙️ Configurações")
    
    if st.session_state.vector_db and not st.session_state.editando:
        st.success("Sistema Online (Memória Ativa)")
        if st.button("Mudar Instruções"):
            st.session_state.editando = True
            st.rerun()
            
    elif st.session_state.editando:
        st.warning("MODO DE EDIÇÃO ATIVO")
        novo_arquivo = st.file_uploader("Subir novo Manual (Isso apagará o anterior)", type="pdf")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancelar"):
                st.session_state.editando = False
                st.rerun()
        with col2:
            if st.button("Limpar Memória"):
                if limpar_tudo_e_zerar():
                    st.session_state.editando = False
                    st.rerun()
        
        if novo_arquivo:
            if st.button("Confirmar e Substituir"):
                processar_novo_pdf(novo_arquivo)
    else:
        st.info("Aguardando Manual Inicial")
        arquivo_inicial = st.file_uploader("Carregar PDF", type="pdf")
        if arquivo_inicial and st.button("Iniciar Sistema"):
            processar_novo_pdf(arquivo_inicial)

    st.divider()
    if st.button("Limpar Conversa"):
        st.session_state.mensagens = []
        st.rerun()

# --- ÁREA DE CHAT ---
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Comando..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.mensagens.append({"role": "user", "content": prompt})
    
    if st.session_state.vector_db:
        docs = st.session_state.vector_db.similarity_search(prompt, k=5)
        contexto = "\n\n".join([d.page_content for d in docs])
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        res = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"Você é a M.O.T.H.E.R. Responda usando apenas o contexto: {contexto}"},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant"
        )
        resposta = res.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(resposta)
            with st.expander("O que eu li agora:"):
                st.code(contexto)
        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
    else:
        st.error("Erro: Sistema sem memória. Carregue um PDF.")