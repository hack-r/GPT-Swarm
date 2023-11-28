# aux/task_manager.py
from aux.logger import setup_logging
from aux.file_utils import save_to_file
from aux.chat import (
    break_down_tasks,
    combine_and_process_results,
    execute_tasks_in_parallel,
    generate_question_id,
    get_subject,
    monitor_task_completion,
    prime_gpt_with_subject
)

logger = setup_logging()

def run_task_manager(args):
    question_id = generate_question_id()
    subject = get_subject(args.question, args.model)
    if not subject:
        logger.error("Failed to determine the subject.")
        return

    # This function now returns the conversation history
    conversation_history = prime_gpt_with_subject(subject, args.model)
    print("Result of priming: ", conversation_history)

    tasks = break_down_tasks(args.question, args.num_tasks, args.model)
    print("Task list: ", tasks)
    if not tasks:
        logger.error("No tasks were generated from the question.")
        return

    # Pass the conversation history to execute tasks in parallel
    futures = execute_tasks_in_parallel(tasks, conversation_history, subject, args.model)
    task_results = []

    for data in monitor_task_completion(futures):
        task_results.append(data)
        # Save each task result immediately after completion.
        save_to_file(data, question_id)

    # Once all tasks are completed, combine the results.
    final_response = combine_and_process_results(task_results, model="gpt-4")
    # Save the final combined result.
    save_to_file(final_response, "final_" + question_id)
    # Print the final combined response.
    print(final_response)
