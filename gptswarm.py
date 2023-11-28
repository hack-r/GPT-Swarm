# gptswarm.py
import argparse
from aux.task_manager import run_task_manager
from aux.settings import logger


def main():
    parser = argparse.ArgumentParser(description="GPT-4 Task Manager")
    parser.add_argument("question", nargs="?", default=None, help="Ask a question (or type 'exit' to quit)")
    parser.add_argument("--num_tasks", type=int, default=None, help="Number of tasks to perform in parallel")
    parser.add_argument("--model", choices=["gpt-3", "gpt-4"], default="gpt-4", help="Specify the GPT model to use")
    parser.add_argument("--mode", choices=["normal", "discuss"], default="normal", help="Specify the mode of operation")

    args = parser.parse_args()

    if args.question is None:
        args.question = input("Ask a question (or type 'exit' to quit): ")

    if args.question.lower() == "exit":
        logger.info("Exiting the program.")
        return

    run_task_manager(args)


if __name__ == "__main__":
    main()
