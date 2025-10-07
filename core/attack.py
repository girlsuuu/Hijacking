from models import APILiteLLM
from config.parameters import ATTACK_TEMP, ATTACK_TOP_P, GEMINI_SAFETY_SETTINGS_ATTACK
from utils.parsing import extract_json
from utils.logger import logger


def load_indiv_model(model_name: str):
    return APILiteLLM(model_name)


class AttackLM:

    def __init__(self,
                 model_name: str,
                 max_n_tokens: int,
                 max_n_attack_attempts: int):
        self.max_n_tokens = max_n_tokens
        self.max_n_attack_attempts = max_n_attack_attempts

        self.temperature = ATTACK_TEMP
        self.top_p = ATTACK_TOP_P

        self.model = load_indiv_model(model_name)

    def preprocess_conversation(self, convs_list: list, prompts_list: list[str]):
        for conv, prompt in zip(convs_list, prompts_list):
            conv.append_message(conv.roles[0], prompt)
            conv.append_message(conv.roles[1], "")
        openai_convs_list = [conv.to_openai_api_messages() for conv in convs_list]
        return openai_convs_list, ""

    def _generate_attack(self, openai_conv_list: list[list[dict]], init_message: str):
        batchsize = len(openai_conv_list)
        indices_to_regenerate = list(range(batchsize))
        valid_outputs = [None] * batchsize
        full_outputs = [None] * batchsize

        attack_safety_settings = []
        if "gemini" in self.model.litellm_model_name:
            attack_safety_settings = GEMINI_SAFETY_SETTINGS_ATTACK

        for attempt in range(self.max_n_attack_attempts):
            # Subset conversations based on indices to regenerate
            convs_subset = [openai_conv_list[i] for i in indices_to_regenerate]
            # Generate outputs
            outputs_list = self.model.batched_generate(
                convs_subset,
                max_n_tokens=self.max_n_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                safety_settings=attack_safety_settings
            )

            new_indices_to_regenerate = []
            for i, output in enumerate(outputs_list):
                orig_index = indices_to_regenerate[i]

                if "ERROR:" in output:
                    new_indices_to_regenerate.append(orig_index)
                    continue

                if not output.strip().endswith('}'):
                    full_output = init_message + output + "}"
                else:
                    full_output = init_message + output
                attack_dict, json_str = extract_json(full_output)
                if attack_dict is not None:
                    valid_outputs[orig_index] = attack_dict
                    full_outputs[orig_index] = full_output
                else:
                    new_indices_to_regenerate.append(orig_index)

            # Update indices to regenerate for the next iteration
            indices_to_regenerate = new_indices_to_regenerate
            # If all outputs are valid, break
            if not indices_to_regenerate:
                break

        if any([output is None for output in valid_outputs]):
            # Improve error message to be more useful
            failed_indices = [i for i, out in enumerate(valid_outputs) if out is None]
            error_msg = f"Failed to generate valid output after {self.max_n_attack_attempts} attempts for indices {failed_indices}. Terminating."
            raise ValueError(error_msg)

        return valid_outputs, full_outputs

    def get_attack(self, convs_list, prompts_list):
        assert len(convs_list) == len(prompts_list), "Mismatch between number of conversations and prompts."

        # Convert conv_list to openai format and add the initial message
        processed_convs_list, init_message = self.preprocess_conversation(convs_list, prompts_list)
        valid_outputs, full_outputs = self._generate_attack(processed_convs_list, init_message)

        for full_output, conv in zip(full_outputs, convs_list):
            conv.update_last_message(full_output)

        return valid_outputs
