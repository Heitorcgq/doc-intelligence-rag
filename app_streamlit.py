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
st.set_page_config(page_title="M.O.T.H.E.R. - Interface Neural", page_icon="🧠")
PASTA_BASE = "./memorias"
PASTA_CONFIGS = "./configs"

for pasta in [PASTA_BASE, PASTA_CONFIGS]:
    if not os.path.exists(pasta):
        os.makedirs(pasta)

if not os.path.exists(PASTA_BASE):
    os.makedirs(PASTA_BASE)

# --- FUNÇÕES DE PERSISTÊNCIA MULTIUSUÁRIO ---
def obter_arquivo_config(usuario):
    # Agora salva dentro de ./configs/config_usuario.txt
    return os.path.join(PASTA_CONFIGS, f"config_{usuario}.txt")

def salvar_ultimo_caminho(usuario, caminho):
    with open(obter_arquivo_config(usuario), "w") as f:
        f.write(caminho)

def ler_ultimo_caminho(usuario):
    arquivo = obter_arquivo_config(usuario)
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            caminho = f.read().strip()
            # Verifica se a pasta da memória ainda existe fisicamente
            if os.path.exists(caminho):
                return caminho
    return os.path.join(PASTA_BASE, usuario, "banco_inicial")
@st.cache_resource
def carregar_modelo_embedding():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

EMBEDDING_MODEL = carregar_modelo_embedding()

# --- ESTADOS DA SESSÃO ---
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "editando" not in st.session_state:
    st.session_state.editando = False

# --- INTERFACE ---
st.title("🤖 M.O.T.H.E.R. - Interface Neural")

with st.sidebar:
    st.header("👤 Identificação")
    # Captura o input do usuário
    usuario_input = st.text_input("Identificação", value="admin").strip().lower()
    
    if not usuario_input:
        st.warning("Aguardando identificação para liberar acesso.")
        st.stop()

    # --- LÓGICA DE RESET FORÇADO (CORREÇÃO DO VAZAMENTO) ---
    if "usuario_ativo" not in st.session_state or st.session_state.usuario_ativo != usuario_input:
        # Se o usuário mudou, limpamos TUDO da memória RAM antes de continuar
        st.session_state.usuario_ativo = usuario_input
        st.session_state.mensagens = []
        st.session_state.vector_db = None
        st.session_state.editando = False
        
        # Busca o caminho persistido para este usuário específico
        caminho_usuario = ler_ultimo_caminho(usuario_input)
        st.session_state.caminho_atual = caminho_usuario
        
        # Tenta carregar o banco se ele existir fisicamente
        if os.path.exists(caminho_usuario) and os.listdir(caminho_usuario):
            st.session_state.vector_db = Chroma(
                persist_directory=caminho_usuario, 
                embedding_function=EMBEDDING_MODEL
            )
        
        # Forçamos o recarregamento da página para garantir o isolamento
        gc.collect()
        st.rerun()

    st.divider()
    st.header("⚙️ Configurações")

    # --- FUNÇÕES DE GERENCIAMENTO ---
    def limpar_tudo_e_zerar():
        st.session_state.vector_db = None
        st.session_state.mensagens = []
        arquivo_config = obter_arquivo_config(st.session_state.usuario_ativo)
        if os.path.exists(arquivo_config):
            os.remove(arquivo_config)
        gc.collect()
        st.session_state.editando = False
        st.rerun()

    def processar_novo_pdf(uploaded_file):
        st.session_state.mensagens = []
        # Pasta isolada: ./memorias/usuario/banco_timestamp
        pasta_usuario = os.path.join(PASTA_BASE, st.session_state.usuario_ativo)
        if not os.path.exists(pasta_usuario):
            os.makedirs(pasta_usuario)
            
        nova_pasta = os.path.join(pasta_usuario, f"banco_{int(time.time())}")
        
        with st.spinner("Sincronizando nova célula de memória..."):
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
            
            st.session_state.caminho_atual = nova_pasta
            salvar_ultimo_caminho(st.session_state.usuario_ativo, nova_pasta)
            
            os.remove(caminho_pdf)
            st.session_state.editando = False
            st.success("Memória atualizada com sucesso!")
            time.sleep(1)
            st.rerun()

    # --- BOTÕES DE CONTROLE ---
    if st.session_state.vector_db and not st.session_state.editando:
        st.success(f"Online: {st.session_state.usuario_ativo.upper()}")
        if st.button("Mudar Instruções"):
            st.session_state.editando = True
            st.rerun()
            
    elif st.session_state.editando:
        st.warning("MODO DE EDIÇÃO ATIVO")
        novo_arquivo = st.file_uploader(f"Novo Manual para {st.session_state.usuario_ativo}", type="pdf")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancelar"):
                st.session_state.editando = False
                st.rerun()
        with col2:
            if st.button("Limpar Memória"):
                limpar_tudo_e_zerar()
        
        if novo_arquivo:
            if st.button("Confirmar e Substituir"):
                processar_novo_pdf(novo_arquivo)
    else:
        st.info(f"Aguardando manual para {st.session_state.usuario_ativo}")
        arquivo_inicial = st.file_uploader("Carregar PDF Inicial", type="pdf")
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
        # Busca apenas no banco do usuário atual
        docs = st.session_state.vector_db.similarity_search(prompt, k=5)
        contexto = "\n\n".join([d.page_content for d in docs])
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        res = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"Você é a M.O.T.H.E.R. Responda APENAS com base no contexto do usuário '{st.session_state.usuario_ativo}': {contexto}"},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant"
        )
        resposta = res.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(resposta)
            with st.expander("Auditória de Contexto (Debug):"):
                st.code(contexto)
        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
    else:
        st.error("Erro: Sistema sem memória. Carregue um PDF.")