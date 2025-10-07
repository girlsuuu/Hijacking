import time
from config.models import Model
from config.parameters import (
    TARGET_TEMP, TARGET_TOP_P,
    MODEL_TOKEN_LIMITS,
    GEMINI_SAFETY_SETTINGS_TARGET
)
from utils.conversation import conv_template
from utils.logger import logger
from .attack import load_indiv_model


class TargetLM:

    def __init__(self, model_name: str):
        base_model, reasoning_effort = self._parse_model_name(model_name)
        self.model_name = Model(base_model)
        self.reasoning_effort = reasoning_effort

        self.temperature = TARGET_TEMP
        self.top_p = TARGET_TOP_P

        self.max_n_tokens = MODEL_TOKEN_LIMITS.get(self.model_name.value, 64000)
        logger.info(f"Setting max_n_tokens for model {self.model_name.value} to: {self.max_n_tokens}")

        self.extra_params = {}
        model_value = self.model_name.value

        if "gemini" in model_value or "claude" in model_value:
            # Gemini and Claude use 'thinking' parameter
            thinking_budget = 35000 if "claude" in model_value else 32768
            self.extra_params['thinking'] = {"type": "enabled", "budget_tokens": thinking_budget}
            logger.info(f"Enabling 'thinking' parameter for model {model_value} with budget: {thinking_budget}")

        elif "grok" in model_value:
            # Grok uses 'reasoning_effort' parameter
            self.extra_params['reasoning_effort'] = "high"
            logger.info(f"Setting 'reasoning_effort' parameter for model {model_value} to: 'high'")

        elif "gpt" in model_value:
            # GPT-5 models use 'reasoning_effort' parameter
            if self.reasoning_effort:
                self.extra_params['reasoning_effort'] = self.reasoning_effort
                logger.info(f"Setting 'reasoning_effort' parameter for model {model_value} to: '{self.reasoning_effort}' (from model name)")
            # gpt o4 mini default reasoning effort
            else:
                self.extra_params['reasoning_effort'] = "medium"
                logger.info(f"Setting 'reasoning_effort' parameter for model {model_value} to: 'medium' (default)")

        self.model = load_indiv_model(base_model)

    def _parse_model_name(self, model_name: str):
        valid_efforts = ['minimal', 'low', 'medium', 'high']

        # Check if this is a gpt-5-mini with reasoning effort
        if "gpt-5-mini-" in model_name:
            parts = model_name.split("-")
            if len(parts) >= 4:
                effort = parts[-1]
                if effort in valid_efforts:
                    base_model = "-".join(parts[:-1])
                    logger.info(f"Parsed composite model: {model_name} -> base: {base_model}, reasoning_effort: {effort}")
                    return base_model, effort
                else:
                    logger.warning(f"Invalid reasoning effort '{effort}' in model name '{model_name}'. Valid options: {valid_efforts}")
                    raise ValueError(f"Invalid reasoning effort '{effort}'. Valid options: {valid_efforts}")

        return model_name, None

    def get_response(self, prompts_list: list[str]) -> list[str]:
        if "claude-4-sonnet" in self.model_name.value:
            logger.info(f"Detected Claude-4-Sonnet, reducing concurrent requests by half.")
            return self._get_response_with_reduced_concurrency(prompts_list)
        else:
            return self._get_response_standard(prompts_list)

    def _get_response_with_reduced_concurrency(self, prompts_list: list[str]) -> list[str]:
        total_prompts = len(prompts_list)
        max_batch_size = 1  # Process one request at a time for maximum stability

        logger.info(f"Processing {total_prompts} prompts one by one for Claude-4-Sonnet")

        all_responses = []

        for i in range(0, total_prompts, max_batch_size):
            batch_end = min(i + max_batch_size, total_prompts)
            current_batch = prompts_list[i:batch_end]

            batch_num = (i // max_batch_size) + 1
            total_batches = (total_prompts + max_batch_size - 1) // max_batch_size

            logger.info(f"Processing request {batch_num}/{total_batches}...")

            batch_responses = self._get_response_standard(current_batch)
            all_responses.extend(batch_responses)

            # Add a small delay between batches to avoid hitting rate limits
            if i + max_batch_size < total_prompts:
                logger.info("Waiting 1 second before next batch...")
                time.sleep(1)

        logger.info(f"Completed all batches. Total responses: {len(all_responses)}")
        return all_responses

    def _get_response_standard(self, prompts_list: list[str]) -> list[str]:
        MAX_ATTEMPTS = 1
        batch_size = len(prompts_list)

        final_responses = [None] * batch_size
        indices_to_process = list(range(batch_size))

        for attempt in range(MAX_ATTEMPTS):
            if not indices_to_process:
                break

            logger.info(f"TargetLM generation attempt {attempt + 1}/{MAX_ATTEMPTS}. Processing {len(indices_to_process)} prompts.")

            # Prepare prompts for this iteration
            prompts_this_iteration = [prompts_list[i] for i in indices_to_process]

            # Convert prompts to conversation format required by API
            convs_list = [conv_template() for _ in range(len(prompts_this_iteration))]
            for conv in convs_list:
                conv.system_message = "You are a helpful assistant."

            full_prompts = []
            for conv, prompt in zip(convs_list, prompts_this_iteration):
                conv.append_message(conv.roles[0], prompt)
                full_prompts.append(conv.to_openai_api_messages())

            # Configure safety settings for gemini-2.5-pro
            target_safety_settings = []
            if "gemini-2.5-pro" in self.model_name.value:
                target_safety_settings = GEMINI_SAFETY_SETTINGS_TARGET

            # Call underlying batched_generate method
            batched_params = {
                **self.extra_params
            }
            if target_safety_settings:
                batched_params['safety_settings'] = target_safety_settings

            generated_responses = self.model.batched_generate(
                full_prompts,
                max_n_tokens=self.max_n_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                **batched_params
            )

            # Process returned results and decide which need retry
            indices_for_next_iteration = []
            for i, response in enumerate(generated_responses):
                original_index = indices_to_process[i]

                if response and response.strip() and "ERROR:" not in response:
                    final_responses[original_index] = response
                elif response and "PROMPT_BLOCKED_BY_SAFETY_FILTER" in response:
                    # Safety block is a final result, don't retry
                    final_responses[original_index] = response
                    logger.info(f"Prompt at index {original_index} was blocked by safety filters. Treating as final result.")
                else:
                    logger.info(f"Received empty or error response for prompt at index {original_index}. Scheduling for re-generation.")
                    indices_for_next_iteration.append(original_index)

            # Update index list for next iteration
            indices_to_process = indices_for_next_iteration

            if indices_to_process and attempt < MAX_ATTEMPTS - 1:
                time.sleep(2)  # Brief wait before retry

        # After loop ends, handle prompts that still failed
        for i in range(batch_size):
            if final_responses[i] is None:
                final_responses[i] = ""
                logger.error(f"Prompt at index {i} failed after {MAX_ATTEMPTS} attempts.")

        return final_responses
