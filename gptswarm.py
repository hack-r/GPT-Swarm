import openai
import concurrent.futures
import time
import json
import os

# Assuming you have set your OPENAI_API_KEY as an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

if openai.api_key is None:
    print("Please set your OpenAI API key as an environment variable.")
    exit(1)

# Directory where the results will be stored
results_dir = "results"

def ask_gpt4(question, model="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant and expert at planning software projects."},
                {"role": "user", "content": question},
            ]
        )
        return response.choices[0].message['content']  # directly return the content of the response
    except Exception as e:
        print(f"Error occurred while communicating with the API: {e}")
        raise

def save_to_file(data, file_name):
    try:
        with open(file_name, 'w') as outfile:
            json.dump(data, outfile)
        print(f"Saved data to {os.path.abspath(file_name)}")
    except Exception as e:
        print(f"Error occurred while saving data: {e}")
        raise

def main(question=None):
    if not os.path.exists(results_dir):  # create results directory if it does not exist
        os.makedirs(results_dir)

    if question is None:
        question = input("Ask a question (or type 'exit' to quit): ")

    if question.lower() == "exit":
        return

    # Confirm if the question is about writing software
    confirmation = ask_gpt4(f"Please answer YES or NO, with no additional text or punctuation - is the following question about writing a piece of software?: '{question}'")
    if confirmation is None or confirmation.lower() != "yes":
        # Proceed with normal flow
        tasks = ask_gpt4(f"Break this apart into separate smaller, more manageable tasks that can be worked on in parallel: {question}")
        if tasks is None:
            return  # skip if API call failed

        tasks = tasks.split("\n")  # assuming tasks are separated by newlines
        print(f"GPT-4 has broken the task into {len(tasks)} smaller tasks.")
        print("Starting parallel GPT-4 queries...")
    else:
        print("The question is about writing a piece of software. Emphasizing working code without placeholders.")

        # Adjust subsequent questions to emphasize working code without placeholders
        tasks = ask_gpt4(f'''Break this apart into separate smaller, more manageable code-writing 
                         tasks that can be worked on in parallel, with emphasis on writing working 
                         code without the use of placeholders. Write each task as a ChatGPT
                         prompt wherein you strongly emphasize that you want the reply to be 
                         real code, not pseudocode and not high-level instructions. 
                         Here's the request: {question}''')
        if tasks is None:
            return  # skip if API call failed

        tasks = tasks.split("\n")  # assuming tasks are separated by newlines
        print(f"GPT-4 has broken the task into {len(tasks)} smaller tasks.")
        print("Starting parallel GPT-4 queries with emphasis on working code...")

    start_time = time.time()
    futures = ask_gpt4_parallel(tasks)

    # Monitor the status of the queries
    while not all([future.done() for future in futures]):
        print(f"{sum([future.done() for future in futures])}/{len(tasks)} tasks completed.")
        time.sleep(1)

    print(f"All tasks completed in {time.time() - start_time} seconds.")

    # Save results of each GPT-4 instance as text files
    for i, future in enumerate(futures):
        response = future.result()
        if response is not None:  # skip if API call failed
            filename = os.path.join(results_dir, f"task_{i}_{int(time.time())}.txt")
            save_to_file(response, filename)
            print(f"Task {i+1} completed.")

    # Combine tasks into 1 large query for GPT-4-32k
    combined_tasks = "\n".join([open(os.path.join(results_dir, f"task_{i}_{int(timeMy apologies, it seems the response was cut off. Here is the full updated version of the `main` function:

def main(question=None):
    if not os.path.exists(results_dir):  # create results directory if it does not exist
        os.makedirs(results_dir)

    if question is None:
        question = input("Ask a question (or type 'exit' to quit): ")

    if question.lower() == "exit":
        return

    # Confirm if the question is about writing software
    confirmation = ask_gpt4(f"Please answer YES or NO, with no additional text or punctuation - is the following question about writing a piece of software?: '{question}'")
    if confirmation is None or confirmation.lower() != "yes":
        # Proceed with normal flow
        tasks = ask_gpt4(f"Break this apart into separate smaller, more manageable tasks that can be worked on in parallel: {question}")
        if tasks is None:
            return  # skip if API call failed

        tasks = tasks.split("\n")  # assuming tasks are separated by newlines
        print(f"GPT-4 has broken the task into {len(tasks)} smaller tasks.")
        print("Starting parallel GPT-4 queries...")
    else:
        print("The question is about writing a piece of software. Emphasizing working code without placeholders.")

        # Adjust subsequent questions to emphasize working code without placeholders
        tasks = ask_gpt4(f'''Break this apart into separate smaller, more manageable code-writing 
                         tasks that can be worked on in parallel, with emphasis on writing working 
                         code without the use of placeholders. Write each task as a ChatGPT
                         prompt wherein you strongly emphasize that you want the reply to be 
                         real code, not pseudocode and not high-level instructions. 
                         Here's the request: {question}''')
        if tasks is None:
            return  # skip if API call failed

        tasks = tasks.split("\n")  # assuming tasks are separated by newlines
        print(f"GPT-4 has broken the task into {len(tasks)} smaller tasks.")
        print("Starting parallel GPT-4 queries with emphasis on working code...")

    start_time = time.time()
    futures = ask_gpt4_parallel(tasks)

    # Monitor the status of the queries
    while not all([future.done() for future in futures]):
        print(f"{sum([future.done() for future in futures])}/{len(tasks)} tasks completed.")
        time.sleep(1)

    print(f"All tasks completed in {time.time() - start_time} seconds.")

    # Save results of each GPT-4 instance as text files
    for i, future in enumerate(futures):
        response = future.result()
        if response is not None:  # skip if API call failed
            filename = os.path.join(results_dir, f"task_{i}_{int(time.time())}.txt")
            save_to_file(response, filename)
            print(f"Task {i+1} completed.")

    # Combine tasks into 1 large query for GPT-4-32k
    combined_tasks = "\n".join([open(os.path.join(results_dir, f"task_{i}_{int(time.time())}.txt")).read() for i in range(len(tasks))])

    # Check if the combined_tasks exceed 8000 tokens
    if len(combined_tasks.split()) > 8000:
        # Split the combined tasks into chunks
        chunk_size = 8000  # Define the desired chunk size
        chunks = [combined_tasks[i:i + chunk_size] for i in range(0, len(combined_tasks), chunk_size)]

        print(f"The combined tasks exceed 8000 tokens and will be split into {len(chunks)} chunks.")

        # Send chunks one by one and wait for completion
        for i, chunk in enumerate(chunks):
            final_question = f"I have completed part {i + 1} of the tasks. Here is the chunk: {chunk}."
            if confirmation.lower() == "yes":
                # If it's a programming question
                final_response = ask_gpt4(f"Please make sure your response includes working code for the user in response to a question they've asked: {final_question}", model="gpt-4")
            else:
                # If it's a general question
                final_response = ask_gpt4(final_question, model="gpt-4")
    else:
        # If the combined tasks do not exceed 8000 tokens
        final_question = f"I have completed several related tasks. These are in response to the query: {question}. Here they are: {combined_tasks}. Can you help me combine this information into one coherent answer?"
        if confirmation.lower() == "yes":
            # If it's a programming question
            final_response = ask_gpt4(f"Please make sure your response includes working code for the user in response to a question they've asked: {final_question}", model="gpt-4")
        else:
            # If it's a general question
            final_response = ask_gpt4(final_question, model="gpt-4")

    print(final_response)


if __name__ == "__main__":
    main()
