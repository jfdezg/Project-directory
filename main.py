import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template

# Configuración de directorio para persistencia
VECTORSTORE_DIR = "vectorstore"

# Carga inicial del entorno
load_dotenv()

# Función para extraer texto de PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            content = page.extract_text()
            if content:
                text += content
    return text

# Función para dividir texto en fragmentos
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(text)

# Función para cargar o crear vectorstore
def load_or_create_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    if os.path.exists(VECTORSTORE_DIR):
        vectorstore = FAISS.load_local(VECTORSTORE_DIR, embeddings)
    else:
        vectorstore = FAISS.from_texts(text_chunks, embeddings)
        vectorstore.save_local(VECTORSTORE_DIR)
    return vectorstore

# Función para actualizar el vectorstore si hay nuevos fragmentos
def update_vectorstore_with_new_chunks(new_chunks):
    embeddings = OpenAIEmbeddings()
    if os.path.exists(VECTORSTORE_DIR):
        vectorstore = FAISS.load_local(VECTORSTORE_DIR, embeddings)
        vectorstore.add_texts(new_chunks)
    else:
        vectorstore = FAISS.from_texts(new_chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_DIR)
    return vectorstore

# Crear el modelo conversacional
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

# Lógica para manejar la interacción

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    # Mostrar solo la última pregunta y respuesta para simular estilo chat
    if st.session_state.chat_history:
        user_msg = st.session_state.chat_history[-2].content if len(st.session_state.chat_history) >= 2 else ""
        bot_msg = st.session_state.chat_history[-1].content

        st.write(user_template.replace("{{MSG}}", user_msg), unsafe_allow_html=True)
        st.write(bot_template.replace("{{MSG}}", bot_msg), unsafe_allow_html=True)

# Función principal

def main():
    st.set_page_config(page_title="Chat con tus PDFs", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat con tus PDFs :books:")
    user_question = st.text_input("Haz una pregunta sobre tus documentos:")
    if user_question and st.session_state.conversation:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Tus documentos")
        pdf_docs = st.file_uploader("Sube tus PDFs y pulsa 'Procesar'", accept_multiple_files=True)
        if st.button("Procesar") and pdf_docs:
            with st.spinner("Procesando..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                updated_vectorstore = update_vectorstore_with_new_chunks(text_chunks)
                st.session_state.conversation = get_conversation_chain(updated_vectorstore)

if __name__ == '__main__':
    main()
