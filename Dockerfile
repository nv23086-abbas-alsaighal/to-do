FROM python:3.12-slim

WORKDIR /app

# install runtime dependencies
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy application
COPY app/ .

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["python", "app.py"]
