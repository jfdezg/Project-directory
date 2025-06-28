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

# Cargar API Key
load_dotenv()
st.set_page_config(page_title="Chat con PDFs", page_icon="📄")
st.write(css, unsafe_allow_html=True)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def get_text_chunks(text):
    splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    return splitter.split_text(text)

def get_vectorstore(chunks):
    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(chunks, embeddings)

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever(), memory=memory)

def handle_userinput(user_question):
    response = st.session_state.conversation({"question": user_question})
    chat_history = response["chat_history"]

    for i, msg in enumerate(chat_history):
        template = user_template if i % 2 == 0 else bot_template
        st.write(template.replace("{{MSG}}", msg.content), unsafe_allow_html=True)

# App principal
st.header("Chat con múltiples PDFs 📄🤖")

if "conversation" not in st.session_state:
    st.session_state.conversation = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = None

question = st.text_input("Haz una pregunta sobre tus documentos:")
if question:
    handle_userinput(question)

with st.sidebar:
    st.subheader("Tus documentos")
    pdf_docs = st.file_uploader("Sube tus PDFs", accept_multiple_files=True)
    if st.button("Procesar"):
        with st.spinner("Leyendo PDFs..."):
            raw_text = get_pdf_text(pdf_docs)
            text_chunks = get_text_chunks(raw_text)
            vectorstore = get_vectorstore(text_chunks)
            st.session_state.conversation = get_conversation_chain(vectorstore)
