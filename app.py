import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(
    page_title="ElectroBot (Gemini)",
    page_icon="🤖",
    layout="centered"
)

# 2. Sidebar for API Key
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check if the key is already in secrets
    if "GEMINI_API_KEY" in st.secrets:
        st.success("API Key loaded from secrets! 🔒")
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        # If not found, ask for it manually
        api_key = st.text_input("Enter Gemini API Key", type="password")
        st.caption("Get your key at [aistudio.google.com](https://aistudio.google.com/)")
    
    st.divider()
    st.markdown("Powered by **Gemini 2.5 Flash**")
# --- 3. Initialize Chat History ---
# Make sure this is inside the 'if not in' block!
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. Display Chat Interface (THE MISSING PART) ---
# This loop MUST run every time the script re-runs to draw old bubbles
for message in st.session_state.messages:
    # We need to translate 'model' (Gemini's name) to 'assistant' (Streamlit's name)
    role = "assistant" if message["role"] == "model" else "user"
    
    with st.chat_message(role):
        # Check if 'parts' is a list or string (Gemini can be tricky)
        content = message["parts"]
        if isinstance(content, list):
            content = content[0] # Grab the text from the list
        st.markdown(content)
# ---  Display Chat Interface ---
st.title("⚡ ElectroBot")
st.caption("Ask me about Arduino, ESP32, Sensors, Circuit Design, or Python for Hardware.")

# 5. Handle User Input
if prompt := st.chat_input("How do I connect a DHT11 to ESP32?"):
    if not api_key:
        st.error("Please enter a Gemini API Key in the sidebar.")
        st.stop()

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "parts": prompt})

    # --- SETUP THE BRAIN ---
    try:
        # A. Configure the Key
        genai.configure(api_key=api_key)
        
        # B. Define the Instruction (MUST BE BEFORE THE MODEL)
        system_instruction = """
        You are an expert Embedded Systems Engineer. 
        Your goal is to help users with electronics, microcontrollers (Arduino, ESP32), 
        sensors, and circuit design.
        - Provide C++ (Arduino) or MicroPython code snippets.
        - Be concise and safety-conscious.
        - If the user asks about non-electronics topics, politely refuse.
        """

        # C. Initialize Model (Using a safer model name)
        # Note: If 'gemini-1.5-flash-latest' fails, try 'gemini-pro'
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )

        # --- GENERATE RESPONSE ---
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Create a chat session with history (excluding the last prompt we just added)
            chat = model.start_chat(history=st.session_state.messages[:-1])
            
            # Send the new message with streaming
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # Save response to history
        st.session_state.messages.append({"role": "model", "parts": full_response})

    except Exception as e:

        st.error(f"Error: {e}")
