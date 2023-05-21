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

    tasks = ask_gpt4(question)
    if tasks is None:
        return  # skip if API call failed

    tasks = tasks.split("\n")  # assuming tasks are separated by newlines
    print(f"GPT-4 has broken the task into {len(tasks)} smaller tasks.")
    print("Starting parallel GPT-4 queries...")

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(ask_gpt4, task) for task in tasks]

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            response = future.result()
            if response is not None:  # skip if API call failed
                filename = os.path.join(results_dir, f"task_{i}_{int(time.time())}.txt")
                save_to_file(response, filename)
                print(f"Task {i+1} completed.")

    print(f"All tasks completed in {time.time() - start_time} seconds.")

    with open(os.path.join(results_dir, f"final_output_{int(time.time())}.txt"), 'w') as outfile:
        for i in range(len(tasks)):
            with open(os.path.join(results_dir, f"task_{i}_{int(time.time())}.txt")) as infile:
                outfile.write(infile.read())

    print("All tasks have completed. The combined response from GPT-4 is saved in the 'results' directory.")

if __name__ == "__main__":
    main()
