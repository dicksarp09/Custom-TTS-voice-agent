"""
AWS Lambda handler for SiriusMed Voice Agent.
This is the entry point for Lambda execution.
"""

import os
import logging
from livekit.agents import WorkerOptions, cli

# Import your agent
from src.siriusmed_gemini_agent import entrypoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    AWS Lambda entry point for the SiriusMed agent.
    
    This handler receives invocations from LiveKit and runs the agent.
    """
    
    logger.info(f"Lambda invoked with event: {event}")
    logger.info(f"Context: {context}")
    
    try:
        # Run the LiveKit agent worker
        # The CLI will handle WebSocket connection to LiveKit automatically
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
                log_level="info"
            )
        )
        
        return {
            "statusCode": 200,
            "body": "Agent started successfully"
        }
    
    except Exception as e:
        logger.error(f"Error in Lambda handler: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }


if __name__ == "__main__":
    # For local testing
    test_event = {"source": "manual-test"}
    test_context = type('obj', (object,), {'function_name': 'siriusmed-agent'})()
    lambda_handler(test_event, test_context)
