"""
Simple test script to call the SiriusMed agent and verify it speaks.
This connects to LiveKit and triggers the agent.
"""

import asyncio
import os
from livekit import api
from livekit.agents import JobContext, WorkerOptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
    print("ERROR: Missing LiveKit credentials in .env file")
    print("Required: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET")
    exit(1)

async def test_agent():
    """Test the agent by creating a room and checking if it responds."""
    
    print(f"LiveKit URL: {LIVEKIT_URL}")
    print(f"API Key: {LIVEKIT_API_KEY[:10]}...")
    
    # Create LiveKit API client
    lk_api = api.LiveKitAPI(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    
    # Create test room
    room_name = "test-siriusmed-agent"
    print(f"\nCreating test room: {room_name}")
    
    try:
        # Delete room if it exists
        try:
            await lk_api.room.delete_room(room_name)
            print(f"Deleted existing room")
        except:
            pass
        
        # Create new room
        room = await lk_api.room.create_room(room_name)
        print(f"✓ Room created: {room.name}")
        
        # List participants
        participants = await lk_api.room.list_participants(room_name)
        print(f"Current participants: {len(participants)}")
        
        # Wait for agent to join
        print("\nWaiting for agent to join (30 seconds)...")
        for i in range(30):
            await asyncio.sleep(1)
            participants = await lk_api.room.list_participants(room_name)
            agent_count = sum(1 for p in participants if p.is_agent or "agent" in p.identity.lower())
            
            if agent_count > 0:
                print(f"✓ Agent joined! Participants: {len(participants)}")
                for p in participants:
                    print(f"  - {p.identity} (Agent: {p.is_agent})")
                
                print("\n🎙️ Agent should be speaking now!")
                print("Listen for Nigerian-accented voice greeting from Sirius...")
                
                # Keep room alive for 10 more seconds to hear response
                await asyncio.sleep(10)
                break
            else:
                print(f"Waiting... ({i+1}/30) - Participants: {len(participants)}")
        else:
            print("⚠️ Agent did not join within 30 seconds")
            print("Check that the agent process is running")
        
        # Cleanup
        print("\nCleaning up...")
        await lk_api.room.delete_room(room_name)
        print("✓ Room deleted")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("SiriusMed Agent Test")
    print("=" * 60)
    asyncio.run(test_agent())
