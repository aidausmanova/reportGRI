# Use an official Python runtime as a parent image
FROM python:3.12-bullseye

# Set the working directory in the container
WORKDIR /backend

# Install the dependencies
COPY requirements.txt /backend/
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY ./ /backend/

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
