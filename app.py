import os
from dotenv import load_dotenv
import openai 
import streamlit as st
import pinecone
import requests
from streamlit_chat import message

load_dotenv()

st.set_page_config(
    page_title="AI Safety Q&A (early prototype)",
    page_icon=":robot:"
)

st.header('AI Safety Q&A')
st.markdown('This is a very **early prototype**. Please do not share this link widely. [Feedback](https://docs.google.com/forms/d/e/1FAIpQLSctk0DpGo3xWazfVDryz42_5aGa9A4vaCJ_W_iKGxpCGWGYkQ/viewform) welcomed!')

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

openai.api_key = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY: str = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX = None
FILTER = {'url': {'$ne': ''}}
INDEX = 'alignment-lit'
NAMESPACE = 'extracted-chunks'
DIMS = 768
MAX_HISTORY = 2
MODEL = 'gpt-3.5-turbo'
RETRIEVER_URL = "https://retriever-model-t6p37v2uia-uw.a.run.app/"
SYSTEM_MSG = "You are a patient and helpful AI safety research assistant. You use a tone that is technical and scientific."
# PREFIX_MSG = """Given the following extracted parts of a long document and a question, create a final answer using only the content provided. 
#   If you don't know the answer, just say that you don't know. Don't try to add information from outside content."""
PREFIX_MSG = """Given the following links to resources, extracted parts of longer documents, and a question at the end, create a final answer using the links and content provided. 
    If you don't know the answer, just say that you don't know. Don't try to make up an answer."""

@st.cache_resource(show_spinner=False)
def init():
    pinecone.init(api_key=PINECONE_API_KEY, environment='us-west1-gcp')
    index = pinecone.Index(INDEX)
    return index

def generate_response(query, past_user_inputs=[], past_generated_responses=[]):

    messages = [ {"role": "system", "content": SYSTEM_MSG} ]
    num_history = min(len(past_user_inputs), MAX_HISTORY)
    for i in range(-1 * num_history, 0, 1):
        print("i", i)
        messages.append(  {"role": "user", "content": past_user_inputs[i]} )
        messages.append(  {"role": "assistant", "content": past_generated_responses[i]} )

    xq = requests.post(RETRIEVER_URL, json={'query': query}).json()
    result = PINECONE_INDEX.query(xq, namespace=NAMESPACE, filter=FILTER, top_k=5, includeMetadata=True)
    sources = {}

    CONTENT = PREFIX_MSG

    for item in result["matches"]:
        if item["score"] > 0.3:
            CONTENT += "\n\nLINK: " + item["metadata"]["url"]
            CONTENT += "\n\nCONTENT: " + item["metadata"]["text"]
            # print("item score:", item["score"], item["metadata"]["title"], item["metadata"]["url"])
            if len(item["metadata"]["url"]) > 0:
                sources[item["metadata"]["url"]] = item["metadata"]["title"]

    stampy_sources = []
    non_stampy_sources = []
    # order stampy sources first
    for url, title in sources.items():
        if 'aisafety.info' in url:
            stampy_sources.append({'url': url, 'title': title})
        else:
            non_stampy_sources.append({'url': url, 'title': title})
    sources_ordered = stampy_sources + non_stampy_sources
    # print('sources_ordered', sources_ordered)

    CONTENT += f"\n\nQUESTION: {query}"
    CONTENT += "\n\nFINAL ANSWER:"

    messages.append(  {"role": "user", "content": CONTENT} )
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )

    generated_text = (response['choices'][0]['message']['content'])
    # generated_text = result["matches"][0]["metadata"]["text"]
    # print("\n\nmessages", messages)
    return { "generated_text": generated_text, "sources": sources_ordered}

def format_output(result):
    output = result["generated_text"]
    if len(result["sources"]) > 0:
        output += "\n\n**Recommended reading**"
    for source in result["sources"]:
        output += "\n- [" + source['title'] +"](" + source['url'] + ")"
    return output

with st.spinner("Initializing..."):
    PINECONE_INDEX = init()

user_input = st.text_input("What is your question?", value="What is AI Safety?")

if user_input:
    output = generate_response(user_input, st.session_state.past, st.session_state.generated)
    output = format_output(output)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        # message(st.session_state["generated"][i], key=str(i), avatar_style="bottts-neutral", seed="Sugar")
        st.markdown(st.session_state["generated"][i])
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="fun-emoji", seed="Snickers")

