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

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
    return text

def get_text_chunks(text):
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return splitter.split_text(text)

def get_vectorstore(chunks):
    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(chunks, embeddings)

def get_conversation_chain(vstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vstore.as_retriever(),
        memory=memory
    )

def handle_userinput(user_question):
    if st.session_state.conversation is None:
        st.warning("⚠️ Debes subir documentos y pulsar 'Process' primero.")
        return

    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response["chat_history"]

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

def main():
    import os
    from dotenv import load_dotenv

    load_dotenv()
    st.set_page_config(page_title="Chat con PDFs", page_icon="📚")
    # st.write("DEBUG - Clave cargada:", os.getenv("OPENAI_API_KEY"))
    st.write(css, unsafe_allow_html=True)


    st.header("📚 Chat con múltiples PDFs")
    st.markdown("Sube uno o varios archivos PDF desde la barra lateral y haz clic en 'Process'. Luego podrás hacer preguntas.")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    user_question = st.text_input("✍️ Escribe tu pregunta sobre los documentos:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Tus documentos")
        pdf_docs = st.file_uploader("Sube tus PDFs aquí", accept_multiple_files=True)
        if st.button("Process") and pdf_docs:
            with st.spinner("Procesando documentos..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                vectorstore = get_vectorstore(text_chunks)
                st.session_state.conversation = get_conversation_chain(vectorstore)
                st.success("✅ Listo. Ya puedes hacer preguntas.")

if __name__ == '__main__':
    main()
# This code is a Streamlit application that allows users to upload multiple PDF files,