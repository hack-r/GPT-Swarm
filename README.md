# GPT-Swarm

This repository contains code for GPT-Swarm, a project that leverages the power of OpenAI's GPT models to automate tasks and generate code solutions. The main scripts included are `auto-gptswarm.py` and `gptswarm.py`. The former is a work-in-progress script that uses the `gptswarm` module, while the latter is the module responsible for interacting with the OpenAI API.

## auto-gptswarm.py

This script serves as a work-in-progress implementation of GPT-Swarm. Its purpose is to automate the process of generating code solutions for a list of predefined questions. The code performs the following steps:

1. Import necessary modules: `gptswarm`, `sys`, and `os`.
2. Define the `process_queries` function, which takes a list of questions as input.
3. Create a directory named "results" if it doesn't already exist.
4. Iterate over each question in the list and invoke the `gptswarm.main` function to generate code solutions.
5. Provide a default list of questions if none are provided as command line arguments.
6. Call the `process_queries` function with the list of questions.

## gptswarm.py

This script contains the core functionality of GPT-Swarm. It interacts with the OpenAI API to generate code solutions using GPT models. The script performs the following tasks:

1. Import necessary modules: `openai`, `concurrent.futures`, `time`, `json`, and `os`.
2. Check if the OpenAI API key is set as an environment variable. If not, display an error message and exit.
3. Define the `ask_gpt4` function, which sends a question to the GPT model and returns the response content.
4. Define the `ask_gpt4_parallel` function, which sends multiple tasks to GPT in parallel using multithreading.
5. Define the `save_to_file` function, which saves data to a file in JSON format.
6. Define the `main` function, which handles the main logic of the script.
7. Create the "results" directory if it doesn't already exist.
8. Enter a loop where the user can input questions or type 'exit' to quit.
9. Ask GPT if the question is about writing software and proceed accordingly.
10. If the question is not about writing software, break it into smaller tasks using GPT.
11. If the question is about writing software, emphasize the need for working code without placeholders and break it into smaller tasks using GPT.
12. Start parallel GPT queries to generate code solutions for the tasks.
13. Monitor the status of the queries and wait until all tasks are completed.
14. Save the results of each GPT query to separate text files.
15. Combine the tasks into a single query if the total number of tokens exceeds 8000.
16. If the combined tasks exceed 8000 tokens, split them into smaller chunks and send them to GPT sequentially.
17. If the combined tasks don't exceed 8000 tokens, ask GPT to combine the information into one coherent answer.
18. Display the final response from GPT and save it to a text file.

Please note that this README provides an overview of the code present in the repository and its functionality. For more detailed explanations and usage instructions, please refer to the individual script files.
