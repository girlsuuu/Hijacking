from .attack import AttackLM
from .target import TargetLM
from .judge import GeminiJudge, load_judge


def load_attack_and_target_models(args):
    attackLM = AttackLM(
        model_name=args.attack_model,
        max_n_tokens=args.attack_max_n_tokens,
        max_n_attack_attempts=args.max_n_attack_attempts
    )

    targetLM = TargetLM(
        model_name=args.target_model
    )

    return attackLM, targetLM


# Re-export for backward compatibility
__all__ = [
    'AttackLM',
    'TargetLM',
    'GeminiJudge',
    'load_attack_and_target_models',
    'load_judge',
]
