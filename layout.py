import streamlit as st
from streamlit_option_menu import option_menu

from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from pypdf import PdfReader

from database import supabase

from llm import ( 
    chain
)

from helpers.streamlit import (
    add_history_model,
    format_messages_to_db,
    send_messages_to_db
)

if "chat_list" not in st.session_state:
    st.session_state.chat_list = []
    
if "messages_list" not in st.session_state:
    st.session_state.messages_list = []
    
if "disabled" not in st.session_state:
    st.session_state.disabled = True

if "chat_key" not in st.session_state:
    st.session_state.chat_key = ""
    
if "cv" not in st.session_state:
    st.session_state.cv = "nada"

with open("styles/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if not st.session_state.chat_list:
    history = supabase.table("chat_history").select("*").execute().data
    
    for chats in history:
        st.session_state.chat_list.append(chats["chat_name"])
        messages_list = chats["chat_messages"]
    
        add_history_model(
            messages_list=messages_list,
            chat_history=StreamlitChatMessageHistory,
            key=st.session_state.chat_list[-1]
        )

msgs = StreamlitChatMessageHistory(key=st.session_state.chat_key)

@st.experimental_dialog(title="Nome do Chat", width="small")
def define_chat_name():
    st.write("Qual sera o nome do novo chat?")
    if chat_name := st.text_input(""):
        st.session_state.chat_list.append(chat_name)
        st.rerun()


with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        if add_button := st.button("Criar novo chat"):
            define_chat_name()
            
    def on_off():
        if st.session_state.chat_key:
            st.session_state.disabled = True
        else:
            st.session_state.disabled = False

    with col2:
        if delete_button := st.button("Deletar chat", on_click=on_off , disabled=st.session_state.disabled):            
            if st.session_state.chat_key:
                msgs.clear() 
                chat_name = st.session_state.chat_key
                st.session_state.chat_list.remove(chat_name)
                supabase.table("chat_history").delete().eq("chat_name", chat_name).execute()
                st.session_state.chat_key = ""


    def get_chat_selection(key):
        st.session_state.chat_key = st.session_state[key]
        st.session_state.disabled = False

    if st.session_state.chat_list:
        selected = option_menu(
            "Histórico", 
            st.session_state.chat_list,
            on_change=get_chat_selection, 
            key="chats",
            styles={
                "container": {"background-color": "rgb(38, 39, 48)"},        
                "icon": {"visibility": "hidden", "font-size": "0px"},
                "nav-item": {"padding": "5px 0 5px"},
            }
        )

chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history"
)

if st.session_state.chat_key:
    chat_container = st.container(height=680, border=False)
    coln1, coln2 = st.columns((18, 3))

    with chat_container:
        for msg in msgs.messages:
            st.chat_message(msg.type).write(msg.content)
        
    with coln1:
        if prompt := st.chat_input():
            chat_container.chat_message("human").markdown(prompt)
            
            config = {"configurable": {"session_id": "any"}}
            model_response = chain_with_history.invoke({"question": prompt, "CV": st.session_state.cv}, config)
            
            chat_container.chat_message("ai").markdown(model_response.content)

            send_messages_to_db(
                supabase=supabase,
                chat_name=st.session_state.chat_key,
                chat_messages=msgs
            )
    with coln2:
        with st.popover("Upload", use_container_width=False):
            if file := st.file_uploader("Escolha o arquivo que deseja enviar", type="pdf"):
                reader = PdfReader(file)
                pages = reader.pages
                content = ""
                for page in pages: content += page.extract_text()   
                st.session_state.cv = content