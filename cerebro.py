import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÕES ---
# Usamos um modelo leve da HuggingFace para criar os "vetores" (números) do texto.
# Ele roda local no seu PC, não gasta API.
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Pasta onde a memória do bot vai ficar salva
PERSIST_DIRECTORY = "./banco_vetorial"

# Cliente Groq (já conhecido seu)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def aprender_pdf(caminho_pdf):
    print(f"📖 Lendo o arquivo: {caminho_pdf}...")
    
    # 1. Carregar o PDF
    loader = PyPDFLoader(caminho_pdf)
    documentos = loader.load()
    
    # 2. Dividir o texto em pedaços menores (Chunks)
    # A IA não consegue ler um livro inteiro de uma vez, precisa ser em pedaços.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    textos_divididos = text_splitter.split_documents(documentos)
    
    print(f"✂️ Texto dividido em {len(textos_divididos)} pedaços.")
    
    # 3. Criar/Atualizar o Banco Vetorial (ChromaDB)
    # Aqui a mágica acontece: Texto vira Número e é salvo na pasta.
    print("💾 Salvando na memória (Isso pode demorar um pouco na 1ª vez)...")
    db = Chroma.from_documents(
        documents=textos_divididos, 
        embedding=EMBEDDING_MODEL, 
        persist_directory=PERSIST_DIRECTORY
    )
    # Em versões novas do Chroma, ele persiste automático, mas mal não faz.
    print("✅ Aprendizado concluído! O bot já sabe o conteúdo.")

def perguntar_ao_bot(pergunta):
    # 1. Carregar o banco de dados existente
    db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=EMBEDDING_MODEL)
    
    # 2. Buscar os 3 trechos mais parecidos com a pergunta
    docs = db.similarity_search(pergunta, k=5)
    
    if not docs:
        return "Não encontrei nada sobre isso no manual."
    
    # Junta o conteúdo dos pedaços encontrados
    contexto = "\n\n".join([doc.page_content for doc in docs])
    
    # 3. Montar o Prompt para a Groq
    prompt_sistema = f"""
    Você é a M.O.T.H.E.R., a Inteligência Artificial Central da Base Lunar Alpha.
    
    SUAS DIRETRIZES:
    1. Responda baseando-se ESTRITAMENTE no CONTEXTO fornecido abaixo.
    2. Se a informação não estiver no contexto, responda com frieza: "Dados insuficientes no protocolo. Consulte o Comandante."
    3. Seja direta, técnica e um pouco autoritária.
    4. Cite o número da regra ou seção se possível.
    
    DADOS DO SISTEMA (CONTEXTO):
    {contexto}
    """
    
    # 4. Chamar a Groq
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": pergunta}
        ],
        temperature=0.3 # Baixa criatividade para ele ser fiel ao texto
    )
    
    return completion.choices[0].message.content

# --- ÁREA DE TESTE RÁPIDO (Só roda se der Play neste arquivo) ---
if __name__ == "__main__":
    # Descomente a linha abaixo SÓ na primeira vez para ele ler o PDF
    aprender_pdf("manuais/manual_base_lunar.pdf") 
    
    while True:
        pergunta = input("\nPergunte algo sobre o PDF: ")
        if pergunta.lower() == "sair": break
        
        resposta = perguntar_ao_bot(pergunta)
        print("-" * 50)
        print("🤖 BOT:", resposta)
        print("-" * 50)