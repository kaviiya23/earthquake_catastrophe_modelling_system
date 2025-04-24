import os
from pyngrok import ngrok

# Define the port Streamlit runs on
port = 8501

# Open an ngrok tunnel to the streamlit port
public_url = ngrok.connect(port)
print(f"🔗 Public URL: {public_url}")

# Run your Streamlit app
os.system(f"streamlit run app.py --server.port {port}")
