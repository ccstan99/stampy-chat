import openai 
import streamlit as st
import pinecone
import requests
from streamlit_chat import message

st.set_page_config(
    page_title="Chat about AI Safety - Demo",
    page_icon=":robot:"
)

st.header('Chat about AI Safety')

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

openai.api_key = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
INDEX = 'alignment-lit'
NAMESPACE = 'extracted-chunks'
DIMS = 768
MODEL = 'gpt-3.5-turbo'
RETRIEVER_URL = "https://retriever-model-t6p37v2uia-uw.a.run.app/"
SYSTEM_MSG = "You are a patient and helpful AI safety research assistant. You use a tone that is technical and scientific."
# PREFIX_MSG = """Given the following extracted parts of a long document and a question, create a final answer using only the content provided. 
#   If you don't know the answer, just say that you don't know. Don't try to add information from outside content."""
PREFIX_MSG = """Given the following extracted parts of longer documents and a question at the end, create a final answer using the content provided. 
    If you don't know the answer, just say that you don't know. Don't try to make up an answer."""

@st.cache_resource(show_spinner=False)
def init():
    pinecone.init(api_key=PINECONE_API_KEY, environment='us-west1-gcp')
    index = pinecone.Index(INDEX)
    return index

def generate_response(query, past_user_inputs, past_generated_responses, index):

    messages = [ {"role": "system", "content": SYSTEM_MSG} ]
    if len(past_user_inputs) > 0:
        messages.append(  {"role": "user", "content": past_user_inputs[-1]} )
    if len(past_generated_responses) > 0:
        messages.append(  {"role": "assistant", "content": past_generated_responses[-1]} )

    xq = requests.post(RETRIEVER_URL, json={'query': query}).json()
    result = index.query(xq, namespace=NAMESPACE, top_k=5, includeMetadata=True)
    sources = {}

    CONTENT = PREFIX_MSG

    for item in result["matches"]:
        # print("item", item)
        if item["score"] > 0.3:
            CONTENT += "\n\nCONTENT: " + item["metadata"]["text"]
            sources[item["metadata"]["url"]] = item["metadata"]["title"]
        # print("sources", sources)

    CONTENT += f"\n\nQUESTION: {query}"
    CONTENT += "\n\nFINAL ANSWER:"

    messages.append(  {"role": "user", "content": CONTENT} )
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )

    generated_text = (response['choices'][0]['message']['content'])
    # print("\n\nmessages", messages)
    # generated_text = result["matches"][0]["metadata"]["text"]
    return { "generated_text": generated_text, "sources": sources}

def format_output(result):
    output = result["generated_text"]
    if len(result["sources"]) > 0:
        output += "\n\n**Recommended reading**"
    for url, title in result["sources"].items():
        # output += "\n<a href='" + url +"'>" + title + "</a>"
        output += "\n- [" + title +"](" + url + ")"
    return output

with st.spinner("Initializing..."):
    index = init()

user_input = st.text_input("What is your question?", value="What is AI Safety?")

if user_input:
    output = generate_response(user_input, st.session_state.past, st.session_state.generated, index)
    output = format_output(output)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        # message(st.session_state["generated"][i], key=str(i), avatar_style="bottts-neutral", seed="Sugar")
        st.markdown(st.session_state["generated"][i])
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="fun-emoji", seed="Snickers")

