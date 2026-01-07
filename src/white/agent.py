from a2a.server.tasks import TaskUpdater
from a2a.types import Message, Part, TextPart
from a2a.utils import get_message_text

from .player import Player


class Agent:
    """
    White agent that plays as a participant in Spyfall.
    
    This agent receives prompts from the green agent (orchestrator) and uses
    a Player instance with LLM capabilities to generate responses throughout
    the game (initialization, action phases, voting, and dialogue).
    """
    
    def __init__(self):
        self.player = Player()

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """
        Process an incoming message from the game orchestrator and generate a response.

        Args:
            message: The incoming A2A message from the green agent
            updater: A2A task updater for reporting results
            
        This method handles various message types:
        - Initialization: Role and game rule explanations
        - Action prompts: Requests for actions (ask question or guess location)
        - Dialogue updates: Question/answer broadcasts from other players
        - Voting prompts: End-of-game voting for spy identification
        """
        input_text = get_message_text(message)
        # Check if the orchestrator expects a response or just wants to broadcast info
        skip_response = (message.metadata or {}).get("skip_response", False)
        print(">>> " + input_text)
        
        # Get the player's response (or empty string if skip_response=True)
        statement = await self.player.handle(input_text, skip_response=skip_response)
        if not skip_response:
            print("<<< " + statement)

        print("")

        # Return the statement as an artifact for the orchestrator to process
        await updater.add_artifact(
            parts=[Part(root=TextPart(text=statement))],
            name="Response",
        )
