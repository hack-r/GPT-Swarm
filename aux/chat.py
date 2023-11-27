from aux.settings import openai_api_key, setup_logging
from prompts.prompts import (
    task_prompt,
    subject_prompt,
    confirmation_prompt,
    breakdown_prompt,
    prime_subject_prompt
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
            {"role": "system", "content": "You are a helpful assistant."},
            prime_message
        ]
    )
    # Check if the priming was successful before returning the conversation history
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
    breakdown_prompt_full = breakdown_prompt.format(question=question)
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": breakdown_prompt_full}
        ]
    )
    # Check if the breakdown was successful and return the tasks
    if "content" in response.choices[0].message:
        tasks_response = response.choices[0].message['content']
        tasks = tasks_response.split("***---***")
        logger.info(f"Tasks broken down: {tasks}")
        return tasks[:num_tasks] if num_tasks else tasks
    else:
        logger.error("Failed to break down the tasks.")
        return []

def execute_task(task, conversation_history, model):
    # Pass the conversation history and the task to ask_gpt
    return ask_gpt(task, conversation_history, model)


def execute_tasks_in_parallel(tasks, subject, model):
    futures = {}
    conversation_history = prime_gpt_with_subject(subject, model)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for task in tasks:
            # Schedule each task to start with the primed conversation history
            futures[executor.submit(ask_gpt, task, conversation_history, model)] = task
    return futures


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
            logger.error(f"Task '{task}' generated an exception: {exc}")
