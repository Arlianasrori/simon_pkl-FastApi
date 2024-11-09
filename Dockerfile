FROM python:3.12.5

# Install Poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy only the necessary files for installing dependencies
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry shell
# Install dependencies
RUN poetry install --no-dev

RUN source .env

# Install dependencies
RUN pip install uvicorn

# Copy the rest of the application code
COPY . .


# Command to run the application
ENTRYPOINT ["uvicorn", "main:App","--port", "2008", "--reload"]
