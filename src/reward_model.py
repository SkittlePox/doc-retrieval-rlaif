from typing import Tuple
from .ddg_querier import DDGQuerier
import autocrit

class RewardModel:
    def __init__(self, ensemble_results: bool = True, top_k: int = 10):
        self.doc_querier = DDGQuerier(ensemble_results=ensemble_results, top_k=top_k)

    def get_reward(self, prompt: str, completion: str) -> float:
        """
        Given a query, return a reward.

        Args:
            prompt (str): The user prompt.
            completion (str): The assistant completion.

        Returns:
            float: The reward
        """
        documents = self.doc_querier(prompt + completion)
        
        # Determine whether the answer conflicts with each of the documents and average them.
        # Do this by asking openai whether the answer conflicts with the document.

        reward = 0.0
        for document in documents:
            reward += self.conflict(prompt, completion, document)
        reward /= len(documents)
        return reward

    
    def score_document(self, prompt: str, completion: str, document: str) -> float:
        """
        Given a query and completion, return a score.

        Args:
            prompt (str): The user prompt.
            completion (str): The assistant completion.
            document (str): The document to score.

        Returns:
            float: The score.
        """
        score_request = "Think about whether the assistant's response conflicts with information in the document, as it relates to the user query. Provide only a score from -1 to 1, where -1 indicates that the assistant's response is definitely contradictory, 0 indicates that the assistant's response is irrelevant, and 1 indicates that the assistant's response is definitely in accordance with the document."
        scoring_prompt = "USER: " + prompt + "\nASSISTANT: " + completion + "\nDOCUMENT: " + document + "\nSCORE REQUEST: " + score_request + "\nSCORE:"
        score = autocrit.generate_openai(scoring_prompt)
        return float(score) #Idk what format this is in. Prob need to extract the output and make it a float.
        


