task_prompt = ("You are one node in a swarm of AI instances."
               " You are about to be given 1 sub-task of a larger task. "
               "Another AI will attempt to combine your work with the other completed sub-tasks for the user. Ensure "
               "that the response you give is consumable in this form. Do not include any unnecessary narrative, "
               "caveats, or commentary in your reply - focus on providing actionable insights, working code, "
               "or creative answers, as the case may be.")
subject_prompt = "You are a tool that identifies the subject of a request."
confirmation_prompt = "Please answer YES or NO, is the following question about writing a piece of software?:"
breakdown_prompt = (
    "Break down the following question into smaller tasks that can be worked on in PARALLEL. It is critical that you "
    "provide only a parallel-oriented list of tasks, not sequential."
    "Between each task include ***---*** as a delimiter. Here's the question:")
prime_subject_prompt = "Be prepared to answer questions or take requested actions on the following topic:  {subject}."
