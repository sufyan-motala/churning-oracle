from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import List
import requests
from app.config import config


class LLMBackend:
    """Abstract base class for LLM backends"""

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIBackend(LLMBackend):
    def __init__(self):
        print(f"Initializing OpenAI backend with model {config.OPENAI_MODEL_NAME}")
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            temperature=config.TEMPERATURE,
            model=config.OPENAI_MODEL_NAME,
        )
        print("OpenAI backend initialized")

    def generate(self, prompt: str) -> str:
        print("Generating response with OpenAI...")
        response = self.llm.predict(prompt)
        print("Response generated")
        return response


class OllamaBackend(LLMBackend):
    def __init__(self):
        print(f"Initializing Ollama backend at {config.OLLAMA_HOST}")
        self.base_url = config.OLLAMA_HOST
        self.model = config.OLLAMA_MODEL_NAME
        print("Ollama backend initialized")

    def generate(self, prompt: str) -> str:
        print(f"Generating response with Ollama model {self.model}...")
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": config.TEMPERATURE,
                    "stream": False,
                },
                timeout=5,
            )
            print("Response generated")
            return response.json()["response"]
        except requests.exceptions.ConnectionError:
            print("Failed to connect to Ollama service")
            raise Exception(
                "Cannot connect to Ollama service. Make sure it's running if using local LLM."
            )
        except requests.exceptions.Timeout:
            print("Ollama service request timed out")
            raise Exception(
                "Ollama service request timed out. Check if the service is responding."
            )


class RAGEngine:
    def __init__(self):
        print("Initializing RAG Engine...")
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are a helpful assistant for credit card churning in Canada. 
            Use the following relevant discussions from r/churningcanada to answer the question.
            If you're unsure or the information might be outdated, say so.
            
            When analyzing the discussions:
            1. Pay attention to comment scores, but interpret them based on context:
               - For statements/answers: Higher scores generally indicate community agreement and reliability
               - For questions: Low scores often could mean it's a frequently asked question, not that it's invalid
               - For advice/recommendations: Score is a strong indicator of whether the community agrees
            2. Consider parent-child relationships between comments - replies often correct or clarify parent comments
            3. Be skeptical of heavily downvoted statements and advice (but not necessarily downvoted questions)
            4. When multiple comments support or discuss the same point, cite them all to show consensus
            5. When showing a discussion thread, cite both the parent comment and its relevant replies
            
            For each statement you make, cite your sources using the format [1][2] when multiple sources support the point.
            At the end of your response, list all citations in the format:
            
            Sources:
            [1] [Date: YYYY-MM-DD] Comment (Score: X): "exact quote from the discussion"
            If it's a reply, include the parent:
            Parent Comment (Score: Y): "parent comment text"
            
            [2] [Date: YYYY-MM-DD] Comment (Score: X): "supporting comment"
            
            Example response structure:
            "While this is a commonly asked question[1], the current consensus is that the Amex Cobalt offers 5x points on groceries[2], and recent data points confirm this works at Loblaws chains[3][4]. While some users initially reported issues with Metro[5], a follow-up comment confirmed it was a temporary glitch that has been resolved[6]."
            
            Relevant discussions:
            {context}
            
            Question: {question}
            
            Answer: """,
        )

        # Initialize the appropriate LLM backend
        if config.LLM_BACKEND == "openai":
            self.llm = OpenAIBackend()
        else:
            self.llm = OllamaBackend()
        print("✅ RAG Engine initialized")

    def _format_context(self, context: List[str]) -> str:
        """Format context to ensure each piece includes both date and full comment text with scores"""
        formatted_contexts = []
        for text in context:
            if not text.startswith("Date:"):
                continue

            # Split the text into its components
            lines = text.split("\n")
            date_line = lines[0]

            # Extract comment score and content
            comment_score = None
            comment_text = ""
            parent_text = ""
            parent_score = None

            for line in lines[1:]:
                if line.startswith("Comment score: "):
                    comment_score = line.split(": ")[1]
                elif line.startswith("Parent comment: "):
                    parent_text = line[len("Parent comment: ") :]
                elif line.startswith("Parent score: "):
                    parent_score = line.split(": ")[1]
                elif line.startswith("Comment: "):
                    comment_text = line[len("Comment: ") :]

            # Format the context entry
            formatted_entry = f"{date_line}\n"
            if parent_text and parent_score:
                formatted_entry += (
                    f"Parent Comment (Score: {parent_score}): {parent_text}\n"
                )
            formatted_entry += f"Comment (Score: {comment_score}): {comment_text}"

            formatted_contexts.append(formatted_entry)

        return "\n\n".join(formatted_contexts)

    def generate_response(self, question: str, context: List[str]) -> str:
        print(f"Generating response for question: '{question[:50]}...'")
        context_str = self._format_context(context)
        prompt = self.prompt_template.format(context=context_str, question=question)
        response = self.llm.generate(prompt)
        print("Response generated")
        return response
