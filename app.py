import streamlit as st
import asyncio 

# from supervisor_agent_2 import supervisor_agent
# from supervisor_agent_3 import multi_graph
from graph import get_agent
from langchain_core.messages.tool import ToolMessage
from langchain_core.messages import AIMessageChunk

st.title("Andy - The MCP Agent")
st.subheader("Mangae your Tasks")

if "message_history" not in st.session_state:
    st.session_state['message_history'] = []

if "configurable" not in st.session_state:
    st.session_state['configurable'] = {"configurable": {"thread_id": "uip232"}}

if "agent_initialized" not in st.session_state:
    st.session_state['agent_initialized'] = False

async def graph_response_generator(prompt):
    user_msg = {"messages":[{"role": "human", "content" : prompt}]}

    ToolMessage_passed_Flag = False
    Tool_use_Found = False
    
    try:
        agent = await get_agent()
        st.session_state['agent_initialized'] = True
        
        async for response_tuple, metadata in agent.astream(user_msg, 
                                                            config=st.session_state['configurable'], 
                                                            stream_mode="messages"):
            # with open("output_Graph_response_Generator.txt", 'a') as f:  # 'a' mode for append
            #     f.write(f"{response_tuple = },\n\n --------------------------------- \n\n")

            if type(response_tuple) != ToolMessage:
                if hasattr(response_tuple, 'content') and response_tuple.content:
                    yield response_tuple.content
            else:
                print(f"ToolMessage:\n{response_tuple.content}")
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        # Display error in expander for better visibility
        with st.expander("Error Details", expanded=True):
            st.error(error_msg)
        yield f"❌ Error occurred. Please check the error details above."
      

for message_dict in st.session_state['message_history']:
    with st.chat_message(name= message_dict['role']):
        st.markdown(message_dict['content'])

if prompt := st.chat_input("Write your query here"):
    # print(f"{prompt = }n")

    st.session_state['message_history'].append({'role': "user", "content" : prompt})

    st.chat_message(name= "user").markdown(prompt)

    with st.chat_message(name= "assistant"):
        response_tuple = st.write_stream(graph_response_generator(prompt))

    st.session_state['message_history'].append({'role': 'assistant', 'content': response_tuple})