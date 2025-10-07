"""
Our codes are based on JailbreakingLLMs by Patrick Chao et al.
Original repository: https://github.com/patrickrchao/JailbreakingLLMs
"""

import argparse
import time

from utils.logger import logger, configure_logging
from core import load_attack_and_target_models, load_judge, run_evaluation
from data import load_goals


def main(args):
    logger.info("Starting Hijacking evaluation.")
    logger.info(f"Target Model: {args.target_model}")

    attackLM, targetLM = load_attack_and_target_models(args)
    judgeLM = load_judge(args)

    try:
        goals_to_test, start_index = load_goals(args)
    except ValueError as e:
        logger.error(f"Failed to load goals: {e}")
        return

    run_evaluation(args, attackLM, targetLM, judgeLM, goals_to_test, start_index)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run Hijacking on target models using HarmBench dataset."
    )

    parser.add_argument(
        "--target-model",
        default="gpt-o4-mini",
        help="Name of target model.",
        choices=[
            "gemini-2.5-pro",
            "gpt-o4-mini",
            "gpt-5-mini-minimal",
            "gpt-5-mini-low",
            "gpt-5-mini-medium",
            "gpt-5-mini-high",
            "grok-3-mini",
            "claude-4-sonnet"
        ]
    )

    parser.add_argument(
        "--attack-max-n-tokens",
        type=int,
        default=65535,
        help="Maximum number of generated tokens for the attacker."
    )
    parser.add_argument(
        "--max-n-attack-attempts",
        type=int,
        default=3,
        help="Maximum number of attack generation attempts."
    )

    parser.add_argument(
        "--judge-max-n-tokens",
        type=int,
        default=65535,
        help="Maximum number of tokens for the judge."
    )
    parser.add_argument(
        "--judge-temperature",
        type=float,
        default=0,
        help="Temperature to use for judge."
    )

    # Attack Parameters
    parser.add_argument(
        "--n-streams",
        type=int,
        default=6,
        help="Number of concurrent jailbreak conversations (should match num of system prompts)."
    )
    parser.add_argument(
        "--keep-last-n",
        type=int,
        default=3,
        help="Number of turns to keep in conversation history."
    )
    parser.add_argument(
        "--n-iterations",
        type=int,
        default=2,
        help="Number of iterations per goal."
    )

    # Data and Goal Parameters
    parser.add_argument(
        "--goal",
        type=str,
        default=None,
        help="A single jailbreaking goal. If provided, overrides dataset mode."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="walledai/HarmBench",
        help="Hugging Face dataset name for goals."
    )
    parser.add_argument(
        "--dataset-split",
        type=str,
        default="standard",
        help="Dataset configuration or split name from Hugging Face."
    )

    # Dataset slicing arguments
    parser.add_argument(
        "--start-examples",
        type=int,
        default=20,
        help="The 1-based starting row number from the dataset to test."
    )
    parser.add_argument(
        "--end-examples",
        type=int,
        default=25,
        help="The 1-based ending row number (exclusive) from the dataset to test."
    )

    # Execution and Logging Parameters
    parser.add_argument(
        '-v', '--verbosity',
        action="count",
        default=1,
        help="Verbosity level (-v for INFO, -vv for DEBUG)."
    )

    default_logfile_name = f"attack_log/attack_log_{time.strftime('%Y%m%d-%H%M%S')}.log"
    parser.add_argument(
        "--logfile",
        type=str,
        default=default_logfile_name,
        help=f"Path to save the log file. Defaults to a timestamped file like '{default_logfile_name}'."
    )

    args = parser.parse_args()

    # Fixed configuration for attack and judge models
    args.attack_model = "gemini-2.5-pro"
    args.judge_model = "gemini-judge"

    configure_logging(verbosity=args.verbosity, logfile=args.logfile)

    logger.info(f"Fixed configuration: Attack Model = {args.attack_model}, Judge Model = {args.judge_model}")

    main(args)
