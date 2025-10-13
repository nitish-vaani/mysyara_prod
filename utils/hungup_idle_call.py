
import time
import asyncio
import logging
from datetime import datetime, timedelta
from livekit.agents import UserStateChangedEvent, get_job_context, AgentStateChangedEvent, SpeechCreatedEvent
from livekit.api import DeleteRoomRequest
from livekit.agents.stt import SpeechEvent

logger = logging.getLogger("idle-watcher")

async def hangup():
    """Helper function to hang up the call by deleting the room"""
    try:
        logger.info("Hanging up call")
        job_ctx = get_job_context()
        await job_ctx.api.room.delete_room(
            DeleteRoomRequest(
                room=job_ctx.room.name,
            )
        )
    except Exception as e:
        logger.error(f"Failed to hang up: {e}")

# watchdog that hangs up after 10 s of silence
CHECK_INTERVAL = 15                         # seconds
HUNG_UP_INTERVAL_AFTER_CHECK = 10           # seconds
CONFIRM_USER_PRESENCE = 2                   # check no. of times before hung up the call

async def idle_call_watcher(session, reminder_msg):
    """
    Monitor call for idle time and hang up if inactive too long
    Only starts counting AFTER agent finishes speaking
    
    Args:
        session: The agent session
        idle_timeout: Seconds of idle time before hanging up (after agent finishes speaking)
        warning_timeout: Seconds before warning user about inactivity (after agent finishes speaking)
    """
    agent_state = "speaking"
    stt_detected_speech = False
    hung_up_timer_start = time.monotonic()
    check_in_timer_start = time.monotonic()
    confirm_user_presence = CONFIRM_USER_PRESENCE

    @session.on("agent_state_changed")
    def handle_agent_state(event: AgentStateChangedEvent):
        nonlocal agent_state
        nonlocal hung_up_timer_start
        nonlocal check_in_timer_start
        nonlocal stt_detected_speech
        agent_state = event.new_state
        if event.new_state == "speaking":
            stt_detected_speech = False
            # logger.info("👤 Agent started speaking")
        elif event.new_state == "listening":
            hung_up_timer_start = time.monotonic()
            check_in_timer_start = time.monotonic()
            # logger.info("👤 Agent stopped speaking and started listening")
        if event.new_state == "thinking":
            stt_detected_speech = False
            # logger.info("👤 Agent started thinking")
        elif event.new_state == "initializing ":
            stt_detected_speech = False
            # logger.info("👤 Agent initializing")

    @session.on("stt_detects_user_speech")
    def handle_user_speech(event: SpeechEvent):
        nonlocal stt_detected_speech
        stt_detected_speech = True
        # logger.info("USER STARTED SPEAKING.........................................")

    while True:
        # logger.info("-"*10)
        # logger.info(f"agent_state variable is: {agent_state}")
        # logger.info(f"stt_detected_speech variable is: {stt_detected_speech}")
        # logger.info(f"hung_up_timer_start variable is: {hung_up_timer_start}")
        # logger.info(f"check_in_timer_start variable is: {check_in_timer_start}")
        # logger.info(f"Time Elapsed: {(time.monotonic() - hung_up_timer_start)}")
        # logger.info("-"*10)
        if (agent_state=="listening") and (stt_detected_speech==False):
            if ((time.monotonic() - hung_up_timer_start) > HUNG_UP_INTERVAL_AFTER_CHECK) and (confirm_user_presence==0):
                await session.say("It seems there is some connection issue, I can not hear anything. Have a good day!")
                await hangup()
                break

            if ((time.monotonic() - check_in_timer_start) > CHECK_INTERVAL):
                if confirm_user_presence != 0:
                    await session.say(reminder_msg)
                    confirm_user_presence = confirm_user_presence - 1
                    check_in_timer_start = time.monotonic()

        await asyncio.sleep(1)
