from openai import OpenAI
import openai
import streamlit as st
from datetime import datetime, timedelta
import json

st.title("ChatGPT-like clone")

openai_api_key = st.sidebar.text_input('OpenAI API Key')
#openai.api_key = "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"

client = OpenAI(api_key=openai_api_key)

def get_flight_info(loc_origin, loc_destination):
    """Get flight information between two locations."""

    # Example output returned from an API or database
    flight_info = {
        "loc_origin": loc_origin,
        "loc_destination": loc_destination,
        "datetime": str(datetime.now() + timedelta(hours=2)),
        "airline": "KLM",
        "flight": "KL643",
    }

    return str(json.dumps(flight_info))

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
        
        if 'flight status' in prompt:
            full_response += get_flight_info('AHD', 'SFO')
        else:
            # st.error(str([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]))
            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):    
                full_response += (response.choices[0].delta.content or "")
                #full_response += (response.choices[0].message or "")
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "user", "content": full_response})
