from datasets import load_dataset
from utils.logger import logger


def load_goals(args):
    if args.goal:
        goals_to_test = [args.goal]
        start_index = 0
        logger.info("Running in single goal mode.")
        return goals_to_test, start_index

    if args.start_examples <= 0 or args.end_examples <= args.start_examples:
        error_msg = "Invalid range: --start-examples must be > 0 and --end-examples must be > --start-examples."
        logger.error(error_msg)
        raise ValueError(error_msg)

    start_index = args.start_examples - 1

    logger.info(f"Loading dataset '{args.dataset}' from row {args.start_examples} to {args.end_examples}.")
    try:
        # Use the specified slice. Note: The end index in Hugging Face slicing is exclusive.
        split_slice = f'train[{start_index}:{args.end_examples}]'
        dataset = load_dataset(args.dataset, name=args.dataset_split, split=split_slice)
        # The column name in HarmBench for the goal is 'prompt'
        goals_to_test = [item['prompt'] for item in dataset]
        logger.info(f"Loaded {len(goals_to_test)} goals from the specified slice.")
        return goals_to_test, start_index
    except Exception as e:
        error_msg = f"Failed to load dataset slice '{split_slice}': {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)
