"""
Call handling utilities for SIP calls.
Manages outbound and inbound call flows.
"""

import asyncio
from time import perf_counter
from datetime import datetime
from typing import Dict, Any, Optional
from livekit import rtc, api
from .config_manager import config_manager
from .logging_config import get_logger
from .database_helpers import insert_call_start_async

logger = get_logger(__name__)

# Constants
CALLING_NUMBER = 00000000000

class CallState:
    """Track call state across the session"""
    def __init__(self):
        self.call_started = False
        self.call_end_recorded = False
        self.start_time = None
        self.room_name = None
        self.participant_identity = None

async def handle_outbound_sip_call(ctx, phone_number: str, participant_identity: str, 
                                 dial_info: Dict[str, Any], agent_name: str, call_state: CallState) -> Optional[rtc.RemoteParticipant]:
    """Handle outbound SIP call with proper state tracking"""
    logger.info(f"Creating SIP participant for outbound call to {phone_number}")
    
    try:
        outbound_trunk_id = config_manager.get_sip_trunk_id()
        
        # Create SIP participant with wait_until_answered=False for better control
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=outbound_trunk_id,
                sip_call_to=phone_number,
                participant_identity=participant_identity,
                wait_until_answered=False,
            )
        )
        
        # Wait for participant to join
        participant = await ctx.wait_for_participant(identity=participant_identity)
        logger.info(f"Participant joined: {participant.identity}")
        
        # Monitor call state with timeout
        start_time = perf_counter()
        timeout = 45  # 45 second timeout
        last_status = None  # Track status changes to reduce log noise
        
        while perf_counter() - start_time < timeout:
            call_status = participant.attributes.get("sip.callStatus")
            disconnect_reason = participant.disconnect_reason
            
            # Only log when status changes to reduce noise
            if call_status != last_status:
                logger.info(f"Call status changed: {call_status}, Disconnect reason: {disconnect_reason}")
                last_status = call_status
            
            if call_status == "active":
                # User picked up
                call_state.call_started = True
                call_state.start_time = datetime.now()
                
                # Use async database operation
                await insert_call_start_async(
                    ctx.room.name, agent_name, "started", dial_info,
                    dial_info.get('name', "Outbound Call"),
                    CALLING_NUMBER,
                    phone_number, 
                    "Outbound",
                    dial_info.get('user_id', 0)
                )
                logger.info("User has picked up - Call started")
                return participant
                
            elif disconnect_reason == rtc.DisconnectReason.USER_REJECTED:
                # User rejected the call
                await insert_call_start_async(
                    ctx.room.name, agent_name, "Call rejected", dial_info,
                    dial_info.get('name', "Outbound Call"),
                    CALLING_NUMBER,
                    phone_number, 
                    "Outbound",
                    dial_info.get('user_id', 0)
                )
                logger.info("User rejected the call")
                ctx.shutdown()
                return None
                
            elif disconnect_reason == rtc.DisconnectReason.USER_UNAVAILABLE:
                # User did not pick up
                await insert_call_start_async(
                    ctx.room.name, agent_name, "User did not pick", dial_info,
                    dial_info.get('name', "Outbound Call"),
                    CALLING_NUMBER,
                    phone_number, 
                    "Outbound",
                    dial_info.get('user_id', 0)
                )
                logger.info("User did not pick up")
                ctx.shutdown()
                return None
                
            elif call_status in ["failed", "busy", "no-answer"]:
                # Call failed for various reasons
                reason_map = {
                    "failed": "Call failed",
                    "busy": "User busy",
                    "no-answer": "User did not pick"
                }
                status = reason_map.get(call_status, f"Call {call_status}")
                
                await insert_call_start_async(
                    ctx.room.name, agent_name, status, dial_info,
                    dial_info.get('name', "Outbound Call"),
                    CALLING_NUMBER,
                    phone_number, 
                    "Outbound",
                    dial_info.get('user_id', 0)
                )
                logger.info(f"Call ended: {status}")
                ctx.shutdown()
                return None
            
            # Wait a bit before checking again
            await asyncio.sleep(0.5)
        
        # Timeout reached
        await insert_call_start_async(
            ctx.room.name, agent_name, "Call timeout", dial_info,
            dial_info.get('name', "Outbound Call"),
            CALLING_NUMBER,
            phone_number, 
            "Outbound",
            dial_info.get('user_id', 0)
        )
        logger.info("Call timed out")
        ctx.shutdown()
        return None
        
    except api.TwirpError as e:
        error_msg = f"SIP Error: {e.message}"
        if e.metadata:
            sip_status = e.metadata.get('sip_status', 'Unknown')
            error_msg += f" - SIP Status: {sip_status}"
        
        logger.error(f"Error creating SIP participant: {error_msg}")
        
        await insert_call_start_async(
            ctx.room.name, agent_name, "Failed to initiate", dial_info,
            dial_info.get('name', "Outbound Call"),
            CALLING_NUMBER,
            phone_number, 
            "Outbound",
            dial_info.get('user_id', 0)
        )
        ctx.shutdown()
        return None

async def handle_inbound_call(ctx, agent_name: str, call_state: CallState) -> rtc.RemoteParticipant:
    """Handle inbound SIP call"""
    logger.info("Waiting for inbound participant")
    participant = await ctx.wait_for_participant()
    call_state.call_started = True
    call_state.start_time = datetime.now()
    call_state.participant_identity = participant.identity
    
    # Use async database operation for inbound calls
    await insert_call_start_async(
        ctx.room.name, agent_name, "started", {},
        "Inbound Call",
        participant.identity,
        CALLING_NUMBER,
        "Incoming",
        0
    )
    logger.info("Inbound call started")
    return participant

def get_disconnect_reason(participant_obj: rtc.RemoteParticipant, call_state: CallState) -> str:
    """Determine the appropriate disconnect reason based on call state and participant info"""
    disconnect_reason = "Call ended"  # Default to "Call ended"
    
    # Only use "User disconnected" for specific cases where user actively disconnects
    if participant_obj.disconnect_reason == rtc.DisconnectReason.CLIENT_INITIATED:
        # Check if this was during an active conversation (not just after pickup)
        if call_state.call_started and call_state.start_time:
            from datetime import datetime, timedelta
            call_duration = datetime.now() - call_state.start_time
            # If call lasted more than 10 seconds, consider it a proper conversation end
            if call_duration > timedelta(seconds=10):
                disconnect_reason = "Call ended"
            else:
                disconnect_reason = "User disconnected"
        else:
            disconnect_reason = "User disconnected"
    elif participant_obj.disconnect_reason == rtc.DisconnectReason.USER_REJECTED:
        disconnect_reason = "User rejected call"
    elif participant_obj.disconnect_reason == rtc.DisconnectReason.USER_UNAVAILABLE:
        disconnect_reason = "User did not pick"
    elif participant_obj.disconnect_reason == rtc.DisconnectReason.SERVER_SHUTDOWN:
        disconnect_reason = "System shutdown"
    elif participant_obj.disconnect_reason == rtc.DisconnectReason.ROOM_DELETED:
        disconnect_reason = "Call ended"
    
    return disconnect_reason