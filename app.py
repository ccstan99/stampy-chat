import openai 
import streamlit as st
import pinecone
import requests
# from streamlit_chat import message

openai.api_key = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
INDEX = 'alignment-lit'
NAMESPACE = 'extracted-chunks'
DIMS = 768
MODEL = 'gpt-3.5-turbo'
RETRIEVER_URL = "https://retriever-model-t6p37v2uia-uw.a.run.app/"

@st.experimental_singleton(show_spinner=False)
def init():
    pinecone.init(api_key=PINECONE_API_KEY, environment='us-west1-gcp')
    index = pinecone.Index(INDEX)
    return index

def generate_response(query, index):

    xq = requests.post(RETRIEVER_URL, json={'query': query}).json()
    result = index.query(xq, namespace=NAMESPACE, top_k=5, includeMetadata=True)


    CONTENT = "Given the following extracted parts of a long document and a question, create a final answer using only the content provided. If you don't know the answer, just say that you don't know. Don't try to add information from outside content."
    CONTENT += f"\n\nQUESTION: {query}"

    for item in result["matches"]:
        CONTENT += "\n\nCONTENT: " + item["metadata"]["text"]

    CONTENT += "\n\nFINAL ANSWER:"

    # response = openai.ChatCompletion.create(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": "You are a patient and helpful AI safety research assistant. You use a tone that is technical and scientific."},
    #         {"role": "user", "content": CONTENT},
    #     ],
    #     temperature=0,
    # )

    # message = (response['choices'][0]['message']['content'])
    return CONTENT

st.header('Chat about AI Safety Info')
query = st.text_input("What is your question?", value="What is AI Safety?")

with st.spinner("Initializing..."):
    index = init()

# message(retreiver) 
# message("Hello bot!", is_user=True)  # align's the message to the right

st.markdown(generate_response(query, index))
