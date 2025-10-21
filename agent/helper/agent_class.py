"""
MysyaraAgent class definition.
Contains the main agent logic and function tools.
"""

import json
import asyncio
import time

from datetime import datetime
from typing import Any, AsyncIterable
from livekit import rtc
from livekit.agents import (Agent, function_tool, RunContext, llm)
from livekit.agents import ModelSettings, FunctionTool
from utils.hungup_idle_call import hangup
from utils.utils import load_prompt
from utils.preprocess_text_before_tts import preprocess_text
from utils.gpt_inferencer import LLMPromptRunner
from utils.number_to_conversational_string import convert_number_to_conversational
from .config_manager import config_manager
from .call_handlers import CallState
from .database_helpers import insert_call_end_async
from .transcript_manager import transcript_manager
from .logging_config import get_logger
from .rag_connector import enrich_with_rag

logger = get_logger(__name__)

class MysyaraAgent(Agent):
    """Main Mysyara agent class with all business logic and function tools"""
    
    def __init__(
        self,
        *,
        name: str,
        appointment_time: str,
        dial_info: dict[str, Any],
        call_state: CallState,
        prompt_path: str,
    ):
        _prompt = load_prompt(prompt_path, full_path=True)
        _prompt = _prompt.replace("{{phone_string}}", convert_number_to_conversational(dial_info["phone"]))
        _prompt = _prompt.replace("{{phone_numeric}}", dial_info["phone"])
        _prompt = _prompt.replace("{{current_time}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
        # print(_prompt)
        super().__init__(
            instructions=_prompt
        )
        self.name = name
        self.appointment_time = appointment_time
        self.participant: rtc.RemoteParticipant | None = None
        self.dial_info = dial_info
        self.llm_obj = LLMPromptRunner(api_key=config_manager.get_openai_api_key())
        self.call_state = call_state
        self._seen_results = set()

    async def llm_node(
        self,
        chat_ctx: llm.ChatContext,
        tools: list[FunctionTool],
        model_settings: ModelSettings
    ) -> AsyncIterable[llm.ChatChunk]:
        """Custom LLM node implementation"""
        async for chunk in Agent.default.llm_node(self, chat_ctx, tools, model_settings):
            yield chunk

    async def tts_node(
        self, text: AsyncIterable[str], model_settings: ModelSettings
    ) -> AsyncIterable[rtc.AudioFrame]:
        """Custom TTS node with text preprocessing"""
        async def cleaned_text():
            async for chunk in text:
                yield preprocess_text(chunk)

        async for frame in Agent.default.tts_node(self, cleaned_text(), model_settings):
            yield frame

    def set_participant(self, participant: rtc.RemoteParticipant):
        """Set the participant for this agent session"""
        self.participant = participant

    async def record_call_end(self, end_reason: str):
        """Record call end in database asynchronously with optimized queuing"""
        if self.call_state.call_end_recorded or not self.call_state.call_started:
            return
            
        try:
            self.call_state.call_end_recorded = True
            operation_id = await insert_call_end_async(
                self.call_state.room_name,
                end_reason
            )
            logger.info(f"Queued call end recording: {operation_id} - {end_reason}")
        except Exception as e:
            logger.error(f"Failed to queue call end recording: {e}")

    async def on_enter(self):
        """Called when agent enters the conversation"""
        await self.session.say(
            text="Hi! You've reached MySyara, your trusted car care partner. I am Sam, how can I assist you today?",
        )
        agent_name = self.__class__.__name__
        
        # Import here to avoid circular imports
        from .data_entities import UserData
        userdata: UserData = self.session.userdata
        
        if userdata.ctx and userdata.ctx.room:
            await userdata.ctx.room.local_participant.set_attributes(
                {"agent": agent_name}
            )

    def should_transfer_call(self, user_message: str) -> bool:
        """Determine if the call should be transferred based on user message"""
        transfer_keywords = [
            "human agent", "real person", "speak to someone", "transfer me",
            "human representative", "customer service", "manager", "supervisor",
            "not helpful", "can't help", "escalate", "complaint", "connect me"
        ]
        
        user_msg_lower = user_message.lower()
        return any(keyword in user_msg_lower for keyword in transfer_keywords)

    # async def on_user_turn_completed(
    #     self, turn_ctx: ChatContext, new_message: ChatMessage,
    # ) -> None:
    #     """Called when user completes a turn - enriches with RAG content"""
    #     # Import here to avoid circular imports
    #     from .rag_connector import enrich_with_rag
        
    #     rag_content = await enrich_with_rag('/n'.join(new_message.content))
    #     turn_ctx.add_message(
    #         role="assistant", 
    #         content=f"Additional information relevant to the user's next message: {rag_content}"
    #     )
    #     await self.update_chat_ctx(turn_ctx)
    @function_tool
    async def search_mysyara_knowledge_base(self, context: RunContext, query: str):
        """
        Lookup Mysyara knowledge base if extra information is needed for user's query. This method searches documents related to car servicing, pricing, locations etc about Mysyara.
        """
        # Send a verbal status update to the user after a short delay
        async def _speak_status_update(delay: float = 4):
            await asyncio.sleep(delay)
            await context.session.generate_reply(instructions=f"""
                You are searching the knowledge base for \"{query}\" but it is taking a little while.
                Update the user on your progress, but be very brief.
            """)
        status_update_task = asyncio.create_task(_speak_status_update(4))
        all_results = await enrich_with_rag(query)
        # Filter out previously seen results
        new_results = [
            r for r in all_results if r not in self._seen_results
        ]
        
        # If we don't have enough new results, clear the seen results and start fresh
        if len(new_results) == 0:
            return f"No new context found. - 'Tell Client that you are not aware of this and our team will reach out to you on this.'"
        else:
            new_results = new_results[:2]  # Take top 2 new results

        self._seen_results.update(new_results)

        context = ""
        for i, res in enumerate(new_results):
            context = context + "\n context " + str(i) + ": " + res + "\n"

        # Cancel status update if search completed before timeout
        status_update_task.cancel()
        return new_results

    @function_tool
    async def validate_customer_details(self, ctx: RunContext):
        """Validate customer details by extracting entities from conversation"""
        self.session.generate_reply(instructions="Kindly ask customer to wait for few seconds as you are validating the information required for service booking.")
        entities = [
            ('Name', 'What is the name Of the User'),
            ('Mobile_Number', "What is contact mobile number used for booking service?"),
            ('Approximate_Mileage', "What is the mileage on the vehicle"),
            ('Emirates', "what is emirate in UAE where user want services?"),
            ('Location', "What is the location within emirate where user wants car service"),
        ]
        
        from utils.entity_extractor_dynamic_prompt import generate_prompt_to_get_entities_from_transcript
        prompt = generate_prompt_to_get_entities_from_transcript(
            transcript=transcript_manager.get_transcript(), 
            fields=entities
        )
        content = self.llm_obj.run_prompt(prompt)
        
        # Clean up JSON response
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            content = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse entity extraction response: {e}")
            return "noted" # how to handle this case?
        
        # Check for missing information
        not_mentioned_keys = [key for key, val in content.items() if val.get('value') == 'Not Mentioned']
        if not_mentioned_keys:
            ask_about = "\n".join(f"{key}: {value}" for key, value in entities if key in not_mentioned_keys)
            return f"""Ask user about following missing informations: "{ask_about}". Ask casually and be very crisp."""
        
        return "Noted"                        

    @function_tool()
    async def end_call(self, ctx: RunContext):
        """End the call gracefully"""
        participant_id = self.participant.identity if self.participant else 'unknown'
        logger.info(f"Agent initiated call end for {participant_id}")

        await self.record_call_end("Call ended")

        # Wait for current speech to finish
        current_speech = ctx.session.current_speech
        if current_speech:
            await current_speech.wait_for_playout()

        await hangup()
        return "Noted"
    
    @function_tool()
    async def detected_answering_machine(self, ctx: RunContext):
        """Handle answering machine detection"""
        participant_id = self.participant.identity if self.participant else 'unknown'
        logger.info(f"Detected answering machine for {participant_id}")
        
        await self.record_call_end("Answering machine detected")
        await hangup()
        return "Noted"

    @function_tool()
    async def book_appointment(self, ctx: RunContext):
        """Book an appointment for the customer"""
        # This can be expanded with actual booking logic
        logger.info("Booking appointment initiated")
        return "I'll help you book an appointment. Let me get the available slots for you."
    
    # @function_tool()
    # async def transfer_to_human_agent(self, ctx: RunContext, reason: str = "customer_request"):
    #     """Transfer the call to a human agent"""
    #     participant_id = self.participant.identity if self.participant else 'unknown'
    #     logger.info(f"Initiating call transfer for {participant_id}, reason: {reason}")
        
    #     try:
    #         # Import here to avoid circular imports
    #         from .data_entities import UserData
    #         userdata: UserData = ctx.session.userdata
            
    #         if userdata.ctx and userdata.ctx.room:
    #             # Publish transfer request via data channel
    #             transfer_data = {
    #                 "action": "transfer",
    #                 "reason": reason,
    #                 "context": f"Agent transferring call due to: {reason}",
    #                 "timestamp": time.time()
    #             }
                
    #             await userdata.ctx.room.local_participant.publish_data(
    #                 json.dumps(transfer_data).encode('utf-8'),
    #                 reliable=True
    #             )
                
    #             logger.info(f"Transfer request published: {transfer_data}")
                
    #             # Inform the customer
    #             await ctx.session.generate_reply(
    #                 instructions="Tell the customer you are transferring them to a human agent who can better assist them. Keep it brief and professional."
    #             )
                
    #             return "Transfer request initiated"
    #         else:
    #             logger.error("No room context available for transfer")
    #             return "Transfer failed - no room context"
                
    #     except Exception as e:
    #         logger.error(f"Error initiating transfer: {e}")
    #         return "Transfer request failed"

    #     # @function_tool()
    #     # async def get_service_pricing(self, ctx: RunContext):
    #     #     """Get pricing information for services"""
    #     #     # This can be expanded with actual pricing logic
    #     #     logger.info("Service pricing requested")
    #     #     return "Let me get you the latest pricing information for our services."

    @function_tool()
    async def transfer_to_human_agent(self, ctx: RunContext, reason: str = "customer_request"):
        """Transfer the call to a human agent"""
        participant_id = self.participant.identity if self.participant else 'unknown'
        logger.info(f"Initiating call transfer for {participant_id}, reason: {reason}")
        
        try:
            from .data_entities import UserData
            userdata: UserData = ctx.session.userdata
            
            if userdata.ctx and userdata.ctx.room:
                transfer_data = {
                    "action": "transfer",
                    "reason": reason,
                    "context": f"Agent transferring call due to: {reason}",
                    "timestamp": time.time()
                }
                await self.session.say(
                                        text="Sure. I will transfer your call to one of our human agents.",
                                    )
                                            
                await userdata.ctx.room.local_participant.publish_data(
                    json.dumps(transfer_data).encode('utf-8'),
                    reliable=True
                )
                
                logger.info(f"Transfer request published: {transfer_data}")
                return "Transfer initiated - call will be redirected to human agent shortly"
            else:
                logger.error("No room context available for transfer")
                return "Transfer failed - no room context"
                
        except Exception as e:
            logger.error(f"Error initiating transfer: {e}")
            return "Transfer request failed"

def create_mysyara_agent(name: str, appointment_time: str, dial_info: dict[str, Any], 
                        call_state: CallState, prompt_path: str) -> MysyaraAgent:
    """Factory function to create a MysyaraAgent instance"""
    return MysyaraAgent(
        name=name,
        appointment_time=appointment_time,
        dial_info=dial_info,
        call_state=call_state,
        prompt_path=prompt_path
    )
