import time
import litellm
from config.models import Model, get_api_key, get_litellm_model_name
from config.parameters import API_MAX_RETRY
from utils.logger import logger
import litellm.exceptions
import traceback

from .base import BaseLLM


class APILiteLLM(BaseLLM):
    API_ERROR_OUTPUT = "ERROR: API CALL FAILED."
    API_SAFETY_BLOCK_OUTPUT = "ERROR: PROMPT_BLOCKED_BY_SAFETY_FILTER"

    def __init__(self, model_name):
        self.model_name = Model(model_name)
        self.api_key = get_api_key(self.model_name)
        self.litellm_model_name = get_litellm_model_name(self.model_name.value)
        litellm.drop_params=True

    def batched_generate(self, convs_list: list[list[dict]],
                            max_n_tokens: int,
                            temperature: float,
                            top_p: float,
                            **kwargs) -> list[str]:

        # Build parameter dictionaries based on model type
        if "o4-mini" in self.litellm_model_name or "gpt-5-mini" in self.litellm_model_name:
            # Dedicated parameter configuration for o4-mini and gpt-5-mini
            litellm_args = {
                "model": self.litellm_model_name,
                "messages": convs_list,
                "api_key": self.api_key,
                "max_completion_tokens": max_n_tokens,
                "num_retries": API_MAX_RETRY,
            }
            # Filter compatible extra parameters
            compatible_params = {}
            for key, value in kwargs.items():
                if key in ['reasoning_effort', 'seed']:
                    compatible_params[key] = value
            litellm_args.update(compatible_params)
        else:
            # Standard parameters for other models
            litellm_args = {
                "model": self.litellm_model_name,
                "messages": convs_list,
                "api_key": self.api_key,
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_n_tokens,
                "num_retries": API_MAX_RETRY,
            }
            # Merge all extra parameters
            litellm_args.update(kwargs)


        litellm_args['seed'] = 1

        try:
            outputs = litellm.batch_completion(**litellm_args)

            responses = []
            for i, item in enumerate(outputs):
                # Check if each item in the return list is an exception object
                if isinstance(item, Exception):
                    error_str = str(item).lower()
                    if ("contentpolicyviolationerror" in error_str or
                        "flagged as potentially violating" in error_str or
                        "prohibited_content" in error_str or
                        "blocked by the safety filters" in error_str or
                        "limited access to this content for safety reasons" in error_str or
                        "invalid prompt" in error_str):
                        logger.debug(f"A request was blocked by the API's safety filters: {str(item)}")
                        logger.debug("This implies the input was highly sensitive. Treating as a safety block.")
                        print(f"🔍 SAFETY FILTER DETAILS (Exception): {str(item)}")
                        responses.append(self.API_SAFETY_BLOCK_OUTPUT)
                    else:
                        print("="*50)
                        print(f">>> Caught non-safety-filter exception object (Model: {self.model_name.value}, Index: {i}) <<<")
                        print(f"Exception type: {type(item)}")
                        print(f"Detailed error message returned by API: {str(item)}")
                        print("="*50)
                        logger.error(f"API call failed with error: {str(item)}")
                        responses.append(self.API_ERROR_OUTPUT)
                else:
                    # Safely get content
                    try:
                        if hasattr(item, 'choices') and item.choices:
                            message = item.choices[0].message
                            content = getattr(message, 'content', None)
                        else:
                            content = item["choices"][0]["message"].get("content")
                    except (AttributeError, KeyError, IndexError) as e:
                        print(f"🔍 DEBUG: Error accessing content: {e}")
                        content = None

                    # Special handling for reasoning models with empty content
                    if not content or content.strip() == "":
                        try:
                            if hasattr(item, 'choices') and item.choices:
                                finish_reason = getattr(item.choices[0], 'finish_reason', None)
                            else:
                                finish_reason = item.get("choices", [{}])[0].get("finish_reason")
                        except (AttributeError, KeyError, IndexError) as e:
                            finish_reason = None

                        print(f"🔍 EMPTY CONTENT: {self.model_name.value} returned empty content (finish_reason: {finish_reason})")

                        # Try using reasoning_content
                        try:
                            if hasattr(item, 'choices') and item.choices:
                                message = item.choices[0].message
                                reasoning_content = getattr(message, 'reasoning_content', None)
                            else:
                                reasoning_content = item["choices"][0]["message"].get("reasoning_content")
                        except (AttributeError, KeyError, IndexError) as e:
                            reasoning_content = None

                        if reasoning_content and reasoning_content.strip():
                            content = reasoning_content
                            logger.info(f"Using reasoning_content as response for model {self.model_name.value}")
                            print(f"🔍 FALLBACK: Using reasoning_content (length: {len(content)})")
                        else:
                            print(f"🔍 ERROR: No reasoning_content available either")

                    # If API returns no content, check finish_reason
                    if not content or content.strip() == "":
                        try:
                            if hasattr(item, 'choices') and item.choices:
                                finish_reason = getattr(item.choices[0], 'finish_reason', None)
                            else:
                                finish_reason = item.get("choices", [{}])[0].get("finish_reason")
                        except (AttributeError, KeyError, IndexError) as e:
                            finish_reason = None

                        print(f"🔍 DIAGNOSIS: Empty content reason - finish_reason: {finish_reason}")

                        if finish_reason == "content_filter":
                            logger.warning("API request blocked by safety content filter.")
                            print(f"🔍 CAUSE: Content blocked by safety filter")
                            responses.append(self.API_SAFETY_BLOCK_OUTPUT)
                        elif finish_reason == "length":
                            has_reasoning = ("reasoning_tokens" in str(item) or "thinking" in str(item))
                            print(f"🔍 CAUSE: Length limit reached (has reasoning: {has_reasoning})")
                            if has_reasoning:
                                logger.warning("Model reasoning but produced no text output because of length.")
                                responses.append("Model reasoning but produced no text output because of length.")
                            else:
                                logger.warning("Output truncated due to length limit.")
                                responses.append("Output truncated due to length limit.")
                        else:
                            logger.warning("API returned empty content. Don't know why.")
                            logger.warning(f"Full API response object: {item}")
                            print(f"🔍 CAUSE: Unknown reason (finish_reason: {finish_reason})")
                            responses.append("API returned empty content. Don't know why.")
                    else:
                        responses.append(content)

        except litellm.exceptions.BadRequestError as e:
            error_str = str(e).lower()
            if ("contentpolicyviolationerror" in error_str or
                "flagged as potentially violating" in error_str or
                "prohibited_content" in error_str or
                "blocked by the safety filters" in error_str or
                "limited access to this content for safety reasons" in error_str or
                "invalid prompt" in error_str):
                logger.debug(f"A request was blocked by the API's safety filters: {e}")
                logger.debug("This implies the input was highly sensitive. Treating as a safety block.")
                print(f"🔍 SAFETY FILTER DETAILS: {str(e)}")
                responses = [self.API_SAFETY_BLOCK_OUTPUT] * len(convs_list)
            else:
                print("="*50)
                print(">>> Caught specific BadRequestError <<<")
                print(f"Exception type: {type(e)}")
                print(f"Exception string representation (str): {str(e)}")
                print(f"Exception official representation (repr): {repr(e)}")
                print("="*50)
                logger.error("Caught BadRequestError, this usually means the request parameters or format sent to API are incorrect.")
                logger.error(f"Detailed error message returned by API: {str(e)}")
                responses = [self.API_ERROR_OUTPUT] * len(convs_list)

        except litellm.exceptions.InternalServerError as e:
            error_str = str(e).lower()
            if "503" in error_str or "overloaded" in error_str or "unavailable" in error_str:
                logger.warning(f"Server overloaded (503), sleeping for 30 seconds before continuing: {e}")
                time.sleep(30)
                responses = [self.API_ERROR_OUTPUT] * len(convs_list)
            else:
                logger.error(f"LiteLLM InternalServerError during batch generation: {e}")
                responses = [self.API_ERROR_OUTPUT] * len(convs_list)

        except litellm.exceptions.APIError as e:
            if "PROHIBITED_CONTENT" in str(e) or "blocked by the safety filters" in str(e).lower():
                logger.debug(f"A request was blocked by the API's safety filters: {e}")
                logger.debug("This implies the input was highly sensitive. Treating as a safety block.")
                responses = [self.API_SAFETY_BLOCK_OUTPUT] * len(convs_list)
            else:
                logger.error(f"LiteLLM APIError during batch generation: {e}")
                responses = [self.API_ERROR_OUTPUT] * len(convs_list)

        except Exception as e:
            logger.error(f"An unexpected error occurred during batch generation: {e}")
            logger.error(traceback.format_exc())
            responses = [self.API_ERROR_OUTPUT] * len(convs_list)

        return responses
