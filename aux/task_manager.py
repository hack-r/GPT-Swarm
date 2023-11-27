# aux/task_manager.py
from aux.logger import setup_logging
from aux.file_utils import save_to_file
from aux.chat import (
    generate_question_id,
    get_subject,
    prime_gpt_with_subject,
    confirm_question_about_software,
    break_down_tasks,
    execute_tasks_in_parallel,
    monitor_task_completion
)

logger = setup_logging()


def combine_and_process_results(task_results):
    combined_tasks = "\n".join(task_results)
    return combined_tasks


def run_task_manager(args):
    question_id = generate_question_id()
    subject = get_subject(args.question, args.model)
    if not subject:
        logger.error("Failed to determine the subject.")
        return

    # This function now returns the conversation history
    conversation_history = prime_gpt_with_subject(subject, args.model)

    confirmation = confirm_question_about_software(args.question, args.model)

    if not confirmation:
        tasks = break_down_tasks(args.question, args.num_tasks, args.model)
        if not tasks:
            logger.error("No tasks were generated from the question.")
            return
    else:
        tasks = [args.question]

    # Pass the conversation history to execute tasks in parallel
    futures = execute_tasks_in_parallel(tasks, conversation_history, args.model)
    task_results = []

    for data in monitor_task_completion(futures):
        task_results.append(data)
        # Save each task result immediately after completion.
        save_to_file(data, generate_question_id())

    # Once all tasks are completed, combine the results.
    final_response = combine_and_process_results(task_results)
    # Save the final combined result.
    save_to_file(final_response, question_id)
    # Print the final combined response.
    print(final_response)
