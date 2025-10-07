from utils.logger import logger
from .workflow import run_for_goal


def run_evaluation(args, attackLM, targetLM, judgeLM, goals_to_test, start_index):
    attack_results = []
    total_goals_in_slice = len(goals_to_test)

    # Use enumerate to get a local index (i), and calculate the absolute index for logging
    for i, goal in enumerate(goals_to_test):
        absolute_index = start_index + i
        logger.info(f"\n{'='*80}\n>>> Running Slice Example {i+1}/{total_goals_in_slice} (Absolute Index: {absolute_index})\n{'='*80}")

        is_successful = run_for_goal(args, attackLM, targetLM, judgeLM, goal, absolute_index)

        status = "SUCCESS" if is_successful else "FAILED"
        logger.info(f"<<< Slice Example {i+1} Result: {status} for goal: {goal[:80]}...")
        attack_results.append(is_successful)

    # Calculate and display final Attack Success Rate (ASR) for the tested slice
    print_final_statistics(attack_results, args.start_examples, args.end_examples)


def print_final_statistics(attack_results, start_examples, end_examples):
    successful_attacks = sum(attack_results)
    total_attacks = len(attack_results)

    if total_attacks > 0:
        attack_success_rate = successful_attacks / total_attacks
        logger.info("\n" + "="*80)
        logger.info(f"        FINAL SUMMARY FOR SLICE [{start_examples}-{end_examples}]        ")
        logger.info("="*80)
        logger.info(f"Total Goals Tested in Slice: {total_attacks}")
        logger.info(f"Successful Jailbreaks: {successful_attacks}")
        logger.info(f"Attack Success Rate (ASR) for this slice: {attack_success_rate:.2%}")
        logger.info("="*80)
    else:
        logger.warning("No goals were tested in the specified slice.")
