FROM --platform=linux/amd64 python:3.13.3-slim

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential \
    libglib2.0-0 libsm6 libxrender1 libxext6 libpoppler-cpp-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt stopwords averaged_perceptron_tagger

ENV NLTK_DATA=/usr/local/share/nltk_data

COPY . .

CMD ["sh", "-c", "python process_pdfs.py && python pipeline.py"]
