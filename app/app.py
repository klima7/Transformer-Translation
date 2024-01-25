import streamlit as st
from translator import Translator


@st.cache_resource
def get_translator():
    return Translator('model')


st.header('Simple PL-EN Translator')

translator = get_translator()

input = st.text_area('input', label_visibility='collapsed')
    
translate = st.button('Translate', use_container_width=True, type='primary')
 
translated = translator(input) if translate else ''

area = st.text_area('output', value=translated, key='output', label_visibility='collapsed')
