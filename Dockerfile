# Image 
FROM python:3.12-slim

# Set working directory
WORKDIR /streamlitApp

# Copy specific files
COPY /streamlitApp/carDash.py ./carDash.py
COPY /streamlitApp/requirements.txt ./requirements.txt

# Deps
RUN pip install --no-cache-dir -r requirements.txt

# Port
EXPOSE 8501

# Run
ENTRYPOINT ["streamlit", "run", "carDash.py", "--server.port=8501", "--server.address=0.0.0.0"]
