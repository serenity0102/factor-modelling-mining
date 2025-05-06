FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY src/factor-modeling-model/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire factor-modeling-model directory
COPY src/factor-modeling-model/ .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Use CMD instead of ENTRYPOINT to allow AWS Batch to override
CMD ["python", "run_factor_analysis.py"]
