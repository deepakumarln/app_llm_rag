FROM python:3.12-slim-bookworm as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set work directory

WORKDIR /code

# Install dependencies
RUN pip install --upgrade pip
#COPY requirements.txt /code/

# Copy the Django project
COPY . /code/ 
RUN pip install --no-cache-dir -r /code/requirements.txt

RUN file="$(ls -lrth /code)" && echo $file
RUN ls -la

FROM base AS final

COPY --from=base /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

WORKDIR /code

#MKDIR /code/data/temp

#MKDIR /code/uploads

COPY . /code/

CMD ["uvicorn", "main:app","--host","0.0.0.0", "--port", "80", "--workers", "2"]
