FROM python:3.8-slim

# Evita bytecode e buffer de output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema necessárias para PyAV e OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos da aplicação
COPY undistorter_service.py .
COPY requirements.txt .
COPY matrix_cams/ /matrix_cams/


# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando padrão de execução
CMD ["python", "undistorter_service.py"]
