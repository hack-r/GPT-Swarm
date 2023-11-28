from aux.settings import openai_api_key, setup_logging
from aux.quality_check import check_task_output as quality_check
from prompts.prompts import (
    task_prompt,
    subject_prompt,
    confirmation_prompt,
    breakdown_prompt,
    prime_subject_prompt,
    combiner_prompt
)

import concurrent.futures
import openai
import uuid
import time

logger = setup_logging()

def generate_question_id():
    return uuid.uuid4().hex

def ask_gpt(task, conversation_history, model="gpt-4"):
    openai.api_key = openai_api_key
    # Insert the task prompt at the beginning of the conversation history
    conversation = [{"role": "system", "content": task_prompt}] + conversation_history
    conversation.append({"role": "user", "content": task})
    response = openai.ChatCompletion.create(
        model=model,
        messages=conversation
    )
    return response['choices'][0]['message']['content'].strip()


def get_subject(question, model="gpt-4"):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": subject_prompt},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message['content'].strip()

def prime_gpt_with_subject(subject, model):
    logger.info(f"Priming with subject: {subject}")
    prime_message = {"role": "user", "content": prime_subject_prompt.format(subject=subject)}
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Prepare to answer questions on the subject being provided by the user."},
            prime_message
        ]
    )
    if "content" in response.choices[0].message:
        logger.info("Priming successful.")
        return [prime_message]
    else:
        logger.error("Priming failed.")
        return []

def confirm_question_about_software(question, model):
    messages = [
        {"role": "system", "content": confirmation_prompt},
        {"role": "user", "content": question}
    ]
    confirmation = ask_gpt(question, messages, model)
    return confirmation.lower() == "yes"

def break_down_tasks(question, num_tasks, model):
    logger.info("Breaking down the tasks.")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": breakdown_prompt},
            {"role": "user", "content": question}
        ]
    )
    # Check if the breakdown was successful and return the tasks
    print("Breakdown:",  response.choices[0].message)
    if "content" in response.choices[0].message:
        tasks_response = response.choices[0].message['content']
        tasks = tasks_response.split("***---***")
        logger.info(f"Tasks broken down: {tasks}")
        return tasks[:num_tasks] if num_tasks else tasks
    else:
        logger.error("Failed to break down the tasks.")
        return []

#Workhorse
def execute_tasks_in_parallel(tasks, conversation_history, subject, model):
    futures = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks to the executor
        future_to_task = {executor.submit(ask_gpt, task, conversation_history, model): task for task in tasks}

        # As futures complete, apply quality check
        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
            except Exception as exc:
                print(f'Task {task} generated an exception: {exc}')
            else:
                # Apply quality check to the completed task's result
                checked_task = quality_check(result, task)
                # Update the dictionary with the task that passed the quality check
                futures[future] = checked_task
    return futures

# Example modification in the monitor_task_completion function
def monitor_task_completion(futures):
    start_time = time.time()
    for future in concurrent.futures.as_completed(futures):
        task = futures[future]
        try:
            data = future.result()
            elapsed_time = time.time() - start_time
            logger.info(f"Task '{task}' completed in {elapsed_time} seconds.")
            yield data
        except Exception as exc:
            logger.error(f"Task '{task}' generated an exception: {exc}, future ID: {id(future)}.")

def combine_and_process_results(task_results, model):
    combined_tasks = "\n\n **** SUB-TASK RESULT ****".join(task_results)

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": combiner_prompt},
            {"role": "user", "content": combined_tasks}
        ]
    )


    # Assuming the last message is the model's response to the combined tasks
    result_text = response.choices[0].message['content'].strip()

    return result_text