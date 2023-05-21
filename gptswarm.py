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

def main():
    if not os.path.exists(results_dir):  # create results directory if it does not exist
        os.makedirs(results_dir)

    while True:
        question = input("Ask a question (or type 'exit' to quit): ")

        if question.lower() == "exit":
            break

        # Confirm if the question is about writing software
        confirmation = ask_gpt4(f"Please answer YES or NO, with no additional text or punctuation - is the following question about writing a piece of software?: '{question}'")
        if confirmation is None or confirmation.lower() != "yes":
            # Proceed with normal flow
            tasks = ask_gpt4(f"Break this apart into separate smaller, more manageable tasks that can be worked on in parallel: {question}")
            if tasks is None:
                continue  # skip if API call failed

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
                continue  # skip if API call failed

            tasks = tasks.split("\n")  # assuming tasks are separated by newlines
            print(f"GPT-4 has broken the task into {len(tasks)} smaller tasks.")
            print("Starting parallel GPT-4 queries with emphasis on working code...")

        futures = ask_gpt4_parallel(tasks)

        # Monitor the status of the queries
        while not all([future.done() for future in futures]):
            print(f"{sum([future.done() for future in futures])}/{len(tasks)} tasks completed.")
            time.sleep(1)

        print("All tasks completed.")

        # Combine tasks into 1 large query for GPT-4
        combined_tasks = "\n".join([future.result() for future in futures])

        final_question = f"I have completed several related tasks. Here they are: {combined_tasks}. Can you help me combine this information into one coherent answer?"

        # Ask GPT-4 to review and combine the intermediate answers into 1 coherent final answer
        final_response = ask_gpt4(final_question, model="gpt-4")

        # Validate the final output
        snippet = final_response[:100]  # first 100 tokens
        validation = ask_gpt4(f"Does the following appear to be either a detailed code example or useful, actionable instructions for a user in response to a question they’ve asked? Answer YES or NO only: {snippet}")

        # If validation is NO, then ask the question again with extra emphasis
        if validation.lower() == "no":
            final_response = ask_gpt4(f'''Please make sure your response includes detailed code or actionable instructions for a user in response to a question they've asked: {final_question}''', model="gpt-4")

        if final_response is not None:  # skip if API call failed
            print("All tasks have completed. The combined response from GPT-4 is:")
            print(final_response)
            filename = os.path.join(results_dir, f"final_output_{int(time.time())}.txt")
            save_to_file(final_response, filename)


if __name__ == "__main__":
    main()
