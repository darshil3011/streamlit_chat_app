from openai import OpenAI
import openai
import streamlit as st
from datetime import datetime, timedelta
import json

st.title("ChatGPT-like clone")

openai_api_key = st.sidebar.text_input('OpenAI API Key')
#openai.api_key = "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"

client = OpenAI(api_key=openai_api_key)

def get_rag_response(search_params):
    """Get rag response from traversaal API"""

    url = "https://api-ares.traversaal.ai/d/predict"

    payload = { "data": [search_params] }
    headers = {
      "x-api-key": "85R0T2mNbg3GqEo3dhMvt1wElGGTGZSk3aMGLYSV",
      "content-type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)

    return response

function_descriptions = [
    {
        "name": "get_flight_info",
        "description": "Get flight information between two locations",
        "parameters": {
            "type": "object",
            "properties": {
                "loc_origin": {
                    "type": "string",
                    "description": "The departure airport, e.g. DUS",
                },
                "loc_destination": {
                    "type": "string",
                    "description": "The destination airport, e.g. HAM",
                },
            },
            "required": ["loc_origin", "loc_destination"],
        },
    }
]

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo-0613"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role":"user", "content": '''You are a shopping assistant. I will put down a query, based on that query ask me questions to 
    know my preferences and based on that generate response in following format: "Search Completed. product: x, colour: x, size: x, additional details: x, price-range: x". Keep the parameters exactly same.
    In the final response mention Search Completed and then API parameters. Dont add anything extra to the final response except "Search Completed". 
    Dont mention about API to the user. Just ask questions'''})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What are you looking for today ?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        
        message_placeholder = st.empty()
        full_response = ""
        
        if 'Search Completed' in prompt:
            full_response += get_rag_response()
        else:
            # st.error(str([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]))
            response = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ])    
                # if 'Search Completed' in response.choices[0].delta.content:
                #     full_response += 'Got params for API Call'
                # else:
            
            chat_response = str(response.choices[0].message.content)
            if 'Search Completed' in chat_response:
                api_response = get_rag_response(chat_response.split(' Search Completed')[1]):
                full_response += str(api_response)
                
            else:
                full_response += str(response.choices[0].message.content)
                #full_response += (response.choices[0].message or "")
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "user", "content": full_response})
