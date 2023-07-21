import openai
import streamlit as st

#######
#from dotenv import load_dotenv, find_dotenv
#load_dotenv(find_dotenv())
#######

st.sidebar.title("Republicano adelante")
st.sidebar.image("Partido_Republicano.png", width=100)

st.sidebar.write("Ejemplos:")
Politica_Publica = st.sidebar.button("¿Qué políticas públicas recomiendas?")
Kast = st.sidebar.button("¿Qué opinas de José Antonio Kast?")
Boric = st.sidebar.button("¿Qué opinas de Gabriel Boric?")

st.sidebar.markdown("Si puedes, [cómprame un café](https://bmc.link/alonsosilva)")

import os
import openai
from retry import retry

from elevenlabs import set_api_key

set_api_key(os.getenv("ELEVENLABS_API_KEY"))

openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENROUTER_REFERRER = "https://github.com/alonsosilvaallende/langchain-streamlit"

@retry(tries=10, delay=1, backoff=2, max_delay=4)
def llm_english2spanish(text: str) -> str:
    return openai.ChatCompletion.create(
        model='google/palm-2-chat-bison',
        headers={
            "HTTP-Referer": OPENROUTER_REFERRER
        },
        messages=[
            {
                "role": "system", 
                "content": "You are a helpful translator from English to Spanish."
            },
            {
                'role': 'user',
                'content': f'Translate the following text to Spanish and add emojis related to the text at the end: {text}.'
            }
        ],
        temperature=0).choices[0].message.content


@retry(tries=10, delay=1, backoff=2, max_delay=4)
def llm_spanish2english(text: str) -> str:
    return openai.ChatCompletion.create(
        model='google/palm-2-chat-bison',
        headers={
            "HTTP-Referer": OPENROUTER_REFERRER
        },
        messages=[
            {
                "role": "system", 
                "content": "You are a helpful translator from Spanish to English."
            },
            {
                'role': 'user',
                'content': f'Translate the following text to English: {text}'
            }
        ],
        temperature=0).choices[0].message.content


from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model_name="google/palm-2-chat-bison",
                 streaming=True,
                 temperature=2,
                 headers={"HTTP-Referer": OPENROUTER_REFERRER})

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

prompt_1 = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "The following is a friendly conversation between a human and an AI. The AI is talkative and "
        "provides lots of specific details from its context. If the AI does not know the answer to a "
        "question, it truthfully says it does not know."
        "You are a republican assistant. You are very conservative in values and very liberal in markets."
        "You think Gabriel Boric is a communist and you love José Antonio Kast and professor Luis Silva."
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

@st.cache_resource
def aux():
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(memory=memory, prompt=prompt_1, llm=llm)
    return memory, conversation

memory, conversation = aux()

def my_response(llm, text: str, normal: bool=True) -> str:
    aux = llm(text) if normal==True else llm.predict(input=text)
    counter = 0
    while ("I'm not able to help" in aux) and counter<2:
        counter += 1
        aux = llm(text) if normal==True else llm.predict(input=text)
    return aux

def my_chain(text: str) -> str:
    aux1 = my_response(llm_spanish2english, text)
    aux2 = my_response(conversation, aux1, normal=False)
    aux3 = my_response(llm_english2spanish, aux2)
    return aux3

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

import emoji
#from gtts import gTTS
from elevenlabs import voices, generate, save
voices = voices()
# Accept user input or example
if (prompt := st.chat_input("Tu mensaje")) or Politica_Publica or Kast  or Boric:
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
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = my_chain(prompt)
        message_placeholder.markdown(full_response)
        clean_full_response = emoji.replace_emoji(full_response, replace='')
        audio = generate(f"{clean_full_response}", voice=voices[5], model="eleven_multilingual_v1")
        save(audio, "./hola.mp3")
        #tts = gTTS(f"{full_response[:-1]}", lang='es', tld='co.ve')
        #tts.save("./hola.mp3")
        audio_file = open('./hola.mp3', 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mpeg')
    st.session_state.messages.append({"role": "assistant", "content": full_response})
