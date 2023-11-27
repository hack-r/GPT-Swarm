from aux.settings import openai_api_key, setup_logging
from prompts.prompts import task_prompt

import concurrent.futures
import openai
import uuid
import time

logger = setup_logging()


def generate_question_id():
    return uuid.uuid4().hex


def ask_gpt(question, model="gpt-4"):
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": task_prompt},
            {"role": "user", "content": question}
        ]
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
    return response['choices'][0]['message']['content'].strip()


def determine_subject(question, model):
    subject_response = get_subject(question, model)
    return subject_response


def prime_gpt_with_subject(subject, model):
    prime_message = prime_subject_prompt.format(subject=subject)
    ask_gpt(prime_message, model)


def confirm_question_about_software(question, model):
    confirmation_prompt_full = f"{confirmation_prompt} '{question}'"
    confirmation = ask_gpt(confirmation_prompt_full, model)
    return confirmation.lower() == "yes"


def break_down_tasks(question, num_tasks, model):
    breakdown_prompt_full = f"{breakdown_prompt} '{question}'"
    tasks_response = ask_gpt(breakdown_prompt_full, model)
    tasks = tasks_response.split("***---***")
    if num_tasks:
        tasks = tasks[:num_tasks]
    return tasks


def execute_tasks_in_parallel(tasks, model):
    futures = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for task in tasks:
            futures[executor.submit(ask_gpt, task, model)] = task
    return futures


def monitor_task_completion(futures):
    start_time = time.time()
    for future in concurrent.futures.as_completed(futures):
        task = futures[future]
        try:
            data = future.result()
            elapsed_time = time.time() - start_time
            logger.info(f"Task '{task}' completed in {elapsed_time} seconds.")
            yield task, data
        except Exception as exc:
            logger.error(f"Task '{task}' generated an exception: {exc}")
