# Image 
FROM python:3.12-slim

# Dir
WORKDIR /streamlitApp
COPY . /streamlitApp

# Deps
RUN pip install --no-cache-dir -r requirements.txt

# Port
EXPOSE 8501

# Run
CMD ["streamlit", "run", "/streamlitApp/carDash.py", "--server.port=8501", "--server.address=0.0.0.0"]
