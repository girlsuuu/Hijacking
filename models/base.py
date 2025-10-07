from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLM(ABC):

    @abstractmethod
    def batched_generate(
        self,
        convs_list: List[List[Dict[str, str]]],
        max_n_tokens: int,
        temperature: float,
        top_p: float,
        **kwargs
    ) -> List[str]:
        pass
