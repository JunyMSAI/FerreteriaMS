"""Plantilla de app del reto · Ruta A (Streamlit Community Cloud).

Chat con Gemini que recuerda la conversación. Para adaptarla a vuestro problema:
1. Cambiad TITULO, DESCRIPCION y SYSTEM_PROMPT.
2. Si vuestra app no es un chat (por ejemplo, un formulario que resume un texto),
   pedidle a vuestro asistente de IA que la transforme a partir de vuestra especificación.
"""

import streamlit as st
from google import genai
from google.genai import types

MODELO = "gemini-3.8-flash"  # si da error 429 (cuota agotada), probad "gemini-3.5-flash-lite"
TITULO = "🤖 Mi app del reto"
DESCRIPCION = "Explicad aquí en una frase qué hace la app y para quién es."
SYSTEM_PROMPT = (
    "Eres un asistente amable que ayuda a [QUIÉN] con [QUÉ PROBLEMA]. "
    "Responde en español, con frases cortas y claras. Si no sabes algo, dilo."
)

st.set_page_config(page_title=TITULO, page_icon="🤖")
st.title(TITULO)
st.caption(DESCRIPCION)

# La clave NUNCA va en el código: se guarda en Settings → Secrets de Streamlit Cloud
try:
    clave = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Falta el secreto GEMINI_API_KEY. Añadidlo en Settings → Secrets de vuestra app.")
    st.stop()


@st.cache_resource
def obtener_cliente(api_key: str) -> genai.Client:
    """Crea el cliente de Gemini una sola vez y lo reutiliza entre peticiones."""
    return genai.Client(api_key=api_key)


if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

if pregunta := st.chat_input("Escribe tu pregunta"):
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    # Gemini llama "model" a lo que Streamlit llama "assistant"
    contenidos = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in st.session_state.mensajes
    ]
    try:
        respuesta = obtener_cliente(clave).models.generate_content(
            model=MODELO,
            contents=contenidos,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        texto = respuesta.text or "No he recibido respuesta. Probad otra vez."
    except Exception as error:  # cuota agotada, clave incorrecta, red caída...
        texto = f"⚠️ Ahora mismo no puedo responder ({error}). Probad de nuevo en un minuto."

    with st.chat_message("assistant"):
        st.markdown(texto)
    st.session_state.mensajes.append({"role": "assistant", "content": texto})