from __future__ import annotations

from livekit.agents import JobContext, cli, WorkerOptions
from .helper.entrypoint_handler import handle_entrypoint

def prewarm_fnc(proc):
    """Prewarm function for session initialization"""
    # proc.userdata["bg_audio_config"] = {
    #     "ambient": [{"clip": "office_ambience", "volume": 1}],
    #     "thinking": [
    #         {"clip": "keyboard_typing", "volume": 0.2},
    #         {"clip": "keyboard_typing2", "volume": 0.2},
    #     ],
    # }
    pass

async def entrypoint(ctx: JobContext):
    """Main entrypoint for the agent - delegates to handler"""
    await handle_entrypoint(ctx)

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm_fnc,
            agent_name="Mysyara Agent",
        )
    )
