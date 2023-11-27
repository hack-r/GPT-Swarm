from aux.logger import setup_logging
from aux.file_utils import save_to_file
from aux.chat import generate_question_id, determine_subject, prime_gpt_with_subject, confirm_question_about_software, \
    break_down_tasks, execute_tasks_in_parallel

import time
import concurrent.futures

logger = setup_logging()


def combine_and_process_results(task_results):
    combined_tasks = "\n".join(task_results)
    return combined_tasks


def run_task_manager(args):
    question_id = generate_question_id()
    subject = determine_subject(args.question, args.model)
    if not subject:
        logger.error("Failed to determine the subject.")
        return

    prime_gpt_with_subject(subject, args.model)

    confirmation = confirm_question_about_software(args.question, args.model)

    if not confirmation:
        tasks = break_down_tasks(args.question, args.num_tasks, args.model)
        if not tasks:
            logger.error("No tasks were generated from the question.")
            return
    else:
        tasks = [args.question]

    start_time = time.time()
    futures = execute_tasks_in_parallel(tasks, args.model)
    task_results = []
    for future in concurrent.futures.as_completed(futures):
        print('Checking task: ' + future.__str__())
        task = futures[future]
        try:
            result = future.result()
            elapsed_time = time.time() - start_time
            logger.info(f"Task '{task}' completed in {elapsed_time} seconds.")
            task_results.append(result)
            # Save each task result immediately after completion.
            save_to_file(result, generate_question_id())
        except Exception as exc:
            logger.error(f"Task '{task}' generated an exception: {exc}")

    # Once all tasks are completed, combine the results.
    final_response = combine_and_process_results(task_results)
    # Save the final combined result.
    save_to_file(final_response, question_id)
    # Print the final combined response.
    print(final_response)
