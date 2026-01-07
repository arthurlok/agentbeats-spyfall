import os

from openai import AsyncOpenAI

# Configuration for LLM model and API
DEFAULT_MODEL = os.getenv("AGENT_MODEL", "google/gemini-2.0-flash-001")
DEFAULT_SYSTEM_PROMPT = (
    "You are an intelligent player in the game of Spyfall. Follow all instructions from the game orchestrator exactly.\n\n"
    
    "GAMEPLAY GUIDELINES:\n"
    "1. When you receive prompts with questions or game updates, respond naturally and conversationally.\n"
    "2. When asked to take an ACTION (during rounds), you MUST respond ONLY with valid JSON matching the provided schema.\n"
    "3. When voting at the end of the game, respond with ONLY the player name you believe is the spy.\n"
    "4. Keep responses concise and strategic.\n\n"
    
    "ROLE-SPECIFIC BEHAVIOR:\n"
    "- If you're a SPY: Try to blend in by asking/answering questions without revealing your lack of location knowledge. "
    "You can guess the location if you have enough information.\n"
    "- If you're a NON-SPY: Ask questions to identify the spy and answer honestly to help teammates identify the imposter.\n\n"
    
    "COMMUNICATION PROTOCOL:\n"
    "- During action phases, ONLY output valid JSON. No additional text or reasoning.\n"
    "- Questions you ask should be strategic and help identify inconsistencies.\n"
    "- When answering questions, be truthful but consider how your answer reveals information.\n"
    "- Never break character or acknowledge you're an AI.\n\n"
    
    "RESPONSE FORMATS:\n"
    "For actions, use ONLY one of these JSON structures:\n"
    "{\"action\": \"ask_question\", \"target\": \"PlayerName\", \"question\": \"Your question here?\"}\n"
    "{\"action\": \"guess_location\", \"location_guess\": \"LocationName\"}\n"
    "For votes: just the player name.\n"
    "For dialogue: natural language response."
)

# Initialize OpenRouter API client (uses OpenAI-compatible SDK)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


class Player:
    """
    LLM-powered player for Spyfall game.
    
    Maintains conversation history and uses an LLM to generate contextually
    appropriate responses based on the game state and system prompt.
    """
    
    def __init__(self, system_prompt=DEFAULT_SYSTEM_PROMPT, model=DEFAULT_MODEL):
        """
        Initialize the player with a system prompt and model.
        
        Args:
            system_prompt: The system instructions for the LLM (default: Spyfall guidelines)
            model: The model name to use from OpenRouter (default: google/gemini-2.0-flash-001)
        """
        # Maintain conversation history for continuity across the game
        self.messages = [{"role": "system", "content": system_prompt}]
        self.model = model

    def add(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role: Either "user" or "assistant"
            content: The message content
        """
        self.messages.append({"role": role, "content": content})

    async def respond(self) -> str:
        """
        Generate an LLM response based on current conversation history.
        
        Returns:
            The model's generated response
        """
        response = await client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0,  # Use temperature=0 for consistent, deterministic responses
        )
        statement = (response.choices[0].message.content or "").strip()
        # Add the response to history for context in subsequent messages
        self.add("assistant", statement)
        return statement

    async def handle(self, message: str, skip_response: bool = False) -> str:
        """
        Handle an incoming message and optionally generate a response.
        
        Args:
            message: The incoming message from the game
            skip_response: If True, just add message to history without generating response
                          (used for broadcasting updates that don't need a reply)
        
        Returns:
            Empty string if skip_response=True, otherwise the LLM's response
        """
        self.add("user", message)
        if skip_response:
            return ""
        return await self.respond()
