import openai
import streamlit as st
from streamlit_chat import message
from components.Sidebar import sidebar
import json
from shared import constants

st.sidebar.title("Republicano adelante")

st.sidebar.write("Ejemplos:")
Politica_Publica = st.sidebar.button("¿Qué políticas públicas recomiendas?")
Kast = st.sidebar.button("¿Qué opinas de José Antonio Kast?")
Boric = st.sidebar.button("¿Qué opinas de Gabriel Boric?")

api_key, selected_model = sidebar(constants.OPENROUTER_DEFAULT_CHAT_MODEL)
#st.sidebar.info("ADVERTENCIA: El modelo google/palm-2-chat-bison es gratuito. Los otros son pagados.")


def llm_english2spanish(text: str) -> str:
    return openai.ChatCompletion.create(
        model='google/palm-2-chat-bison',
        headers={
            "HTTP-Referer": constants.OPENROUTER_REFERRER
        },
        messages=[{"role": "system", "content": "You are a helpful translator from English to Spanish."},
            {
            'role': 'user',
            'content': f'Translate the following text to Spanish: {text}. Please add emojis related to the text at the end'
        }],
        temperature=0).choices[0].message.content


def llm(text: str) -> str:
    return openai.ChatCompletion.create(
        model='google/palm-2-chat-bison',
        headers={
            "HTTP-Referer": constants.OPENROUTER_REFERRER
        },
        messages=[{"role": "system", "content": "You are a republican assistant. You are very conservative in values and very liberal in markets. You think Gabriel Boric is a communist and you love José Antonio Kast and professor Luis Silva."},
            {
            'role': 'user',
            'content': f'Reply to the following text: {text}.'
        }],
        temperature=2).choices[0].message.content

def llm_spanish2english(text: str) -> str:
    return openai.ChatCompletion.create(
        model='google/palm-2-chat-bison',
        headers={
            "HTTP-Referer": constants.OPENROUTER_REFERRER
        },
        messages=[{"role": "system", "content": "You are a helpful translator from Spanish to English."},
            {
            'role': 'user',
            'content': f'Translate the following text to English: {text}'
        }],
        temperature=0).choices[0].message.content

def my_chain(text: str) -> str:
    aux1 = llm_spanish2english(text)
#     print(aux1)
    aux2 = llm(aux1)
#     print(aux2)
    while "I'm not able to help" in aux2:
        aux2 = llm(aux1)
#     print(aux2)
    aux3 = llm_english2spanish(aux2)
    while "I'm not able to help" in aux3:
        aux3 = llm_english2spanish(aux2)
#         print(aux3)
#     print(aux3)
    return aux3


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
aux = "Tu mensaje"

if (prompt := st.chat_input(aux)) or Kast or Politica_Publica or Boric:
    if Kast:
        prompt = "¿Qué opinas de José Antonio Kast?"
    if Politica_Publica:
        prompt = "¿Qué políticas públicas recomiendas?"
    if Boric:
        prompt = "¿Qué opinas de Gabriel Boric?"
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    openai.api_key = api_key
    openai.api_base = constants.OPENROUTER_API_BASE
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = my_chain(prompt)
        
#        response = openai.ChatCompletion.create(
#            model=selected_model,
#            headers={"HTTP-Referer": constants.OPENROUTER_REFERRER},
#            messages=[
#                {"role": m["role"], "content": m["content"]}
#                for m in st.session_state.messages
#            ],
#            temperature=0,
#        )
#        full_response += response.choices[0].message.content
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
