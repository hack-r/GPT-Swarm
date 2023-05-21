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
        return None

def ask_gpt4_parallel(tasks):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(ask_gpt4, task) for task in tasks}
        return futures

def save_to_file(data, file_name):
    try:
        with open(file_name, 'w') as outfile:
            json.dump(data, outfile)
        print(f"Saved data to {os.path.abspath(file_name)}")
    except Exception as e:
        print(f"Error occurred while saving data: {e}")

def main():
    if not os.path.exists(results_dir):  # create results directory if it does not exist
        os.makedirs(results_dir)

    while True:
        question = input("Ask a question (or type 'exit' to quit): ")

        if question.lower() == "exit":
            break

        # Ask GPT-4 to break the question into smaller tasks
        tasks = ask_gpt4(f"Break this apart into separate smaller, more manageable tasks that can be worked on in parallel: {question}")
        if tasks is None:
            continue  # skip if API call failed

        tasks = tasks.split("\n")  # assuming tasks are separated by newlines
        print(f"GPT-4 has broken the task into {len(tasks)} smaller tasks.")
        print("Starting parallel GPT-4 queries...")

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
                filename = os.path.join(results_dir, f"task_{i}.txt")
                save_to_file(response, filename)
                print(f"Task {i+1} completed.")

        # Combine tasks into 1 large query for GPT-4-32k
        combined_tasks = "\n".join([open(os.path.join(results_dir, f"task_{i}.txt")).read() for i in range(len(tasks))])
        final_response = ask_gpt4(f"I have completed the tasks. Here they are: {combined_tasks}. Can you help me combine this information into one coherent answer?", model="gpt-4.0-32k")

        if final_response is not None:  # skip if API call failed
            print("All tasks have completed. The combined response from GPT-4-32k is:")
            print(final_response)

if __name__ == "__main__":
    main()
