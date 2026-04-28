import json
from openai import OpenAI
import os

# Initialize Grok client
client = OpenAI(
    api_key=os.environ['XAI_API_KEY'],
    base_url="https://api.x.ai/v1"
)

def lambda_handler(event, context):
    try:
        # Get the user message from API Gateway
        body = json.loads(event['body'])
        user_message = body.get('message', '')

        # Call Grok
        response = client.chat.completions.create(
            model="grok-4-1-fast-reasoning",   # or grok-beta if you prefer
            messages=[
                {"role": "system", "content": "You are a helpful admin assistant for Quadrant Technologies visitor management system."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        grok_reply = response.choices[0].message.content

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'reply': grok_reply
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
