import streamlit as st
from streamlit_chat import message
import requests

st.set_page_config(
    page_title="AI Safety Q&A (early prototype)",
    page_icon=":robot:"
)

# st.image('stampy-logo-min.svg')
st.header('AI Safety Q&A')
st.markdown(':red[This is a very **early prototype**. Please do not share this link widely. [Feedback](https://docs.google.com/forms/d/e/1FAIpQLSctk0DpGo3xWazfVDryz42_5aGa9A4vaCJ_W_iKGxpCGWGYkQ/viewform) welcomed!]')

hide_menu_style = """
<style>
#MainMenu { visibility: hidden; } 
footer { visibility: hidden; }
</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'prev_input' not in st.session_state:
    st.session_state['prev_input'] = ''

# CHAT_URL = 'http://127.0.0.1:8080/api/chat'
CHAT_URL = 'https://stampy-nlp-t6p37v2uia-uw.a.run.app/api/chat'


def format_output(result):
    output = result["generated_text"]
    if len(result["sources"]) > 0:
        output += "\n\n**Recommended reading**"
    for source in result["sources"]:
        output += "\n- [" + source['title'] + "](" + source['url'] + ")"
    return output


data = {}
with st.expander('More options...', expanded=False):
    all = st.checkbox(
        'Search entire dataset (beyond FAQ, key papers & posts)', value=False)
    data['constrain'] = st.checkbox(
        'Use only content from sources (limits hallucinations but also information)', value=False)
    data['namespace'] = 'all-chunks' if all else 'extracted-chunks'
    data['top_k'] = st.slider('Number of sources to consider',
                              min_value=3, max_value=10, value=5)
    # data['max_history'] = st.slider('Max chat history', min_value=0, max_value=5, value=0)

user_input = st.text_input("Enter your question here",
                           value="What is AI alignment, and why is it important?")

if user_input != st.session_state.prev_input:
    # NEW_URL = CHAT_URL+'?query='+user_input+'&top_k=3'
    # print('NEW_URL', NEW_URL)
    # output = requests.get(NEW_URL).json()
    data['query'] = user_input
    data['past'] = st.session_state.past
    data['generated'] = st.session_state.generated
    output = requests.post(CHAT_URL, data=data).json()

    output = format_output(output)
    st.session_state.prev_input = user_input
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        # message(st.session_state["generated"][i], key=str(i), avatar_style="bottts-neutral", seed="Sugar")
        st.markdown(st.session_state["generated"][i])
        message(st.session_state['past'][i], is_user=True, key=str(
            i) + '_user', avatar_style="fun-emoji", seed="Snickers")
