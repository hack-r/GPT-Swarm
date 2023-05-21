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

    # Set the Auto flag
    Auto = True

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
                if i < len(chunks) - 1:
                    ask_gpt4(f"I have completed part {i + 1} of the tasks. Here is the chunk: {chunk}.")
                else:
                    final_question = f"I have completed part {i + 1} of the tasks. Here is the final chunk: {chunk}. Can you help me combine this information into one coherent answer?"
                    if Auto:
                        final_response = ask_gpt4(final_question, model="gpt-4")
                    else:
                        ask_question = input(f"Final question:\n{final_question}\nDo you want to edit the question? (YES/NO): ")
                        if ask_question.lower() == "yes":
                            edited_question = input("Please provide the edited question: ")
                            final_response = ask_gpt4(edited_question, model="gpt-4")
                        else:
                            final_response = ask_gpt4(final_question, model="gpt-4")
        else:
            final_question = f"I have completed several related code-writing tasks. Here they are: {combined_tasks}. Can you help me combine this information into one coherent answer?"
            if Auto:
                final_response = ask_gpt4(final_question, model="gpt-4")
            else:
                ask_question = input(f"Final question:\n{final_question}\nDo you want to edit the question? (YES/NO): ")
                if ask_question.lower() == "yes":
                    edited_question = input("Please provide the edited question: ")
                    final_response = ask_gpt4(edited_question, model="gpt-4")
                else:
                    final_response = ask_gpt4(final_question, model="gpt-4")

        if final_response is not None:  # skip if API call failed
            print("All tasks have completed. The combined response from GPT-4 is:")
            print(final_response)
            filename = os.path.join(results_dir, f"final_output_{int(time.time())}.txt")
            save_to_file(final_response, filename)


if __name__ == "__main__":
    main()
