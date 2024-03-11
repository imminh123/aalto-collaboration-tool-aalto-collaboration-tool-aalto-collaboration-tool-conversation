# 
FROM python:3.11

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY . /code/app

# Install uvicorn
RUN pip install 'uvicorn[standard]'
RUN pip install websockets
# 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]