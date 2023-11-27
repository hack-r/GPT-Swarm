import os
from aux.logger import setup_logging

logger = setup_logging()

# Set the OpenAI API key from an environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Ensure the API key is available
if openai_api_key is None:
    logger.error("OpenAI API key not found.")
    exit(1)

# Directory for results
results_dir = 'results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

logger = setup_logging()
