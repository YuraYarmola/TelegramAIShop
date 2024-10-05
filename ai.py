import asyncio
import datetime
import json

from openai import OpenAI
import os

from db import FlowerDatabase
from weather import getweather


class Tools:
    async def get_flowers_name_and_count(*args, **kwargs) -> (list[str], bool):
        db = FlowerDatabase()
        flowers = db.get_all_flowers()
        db.close()
        ai_adapted_flowers = [f"ID- {i[0]} Flower - {i[1]} Available - {i[2]} Price for one - {i[3]}" for i in flowers]
        return ai_adapted_flowers, False

    async def calculate_delivery_cost(*args, **kwargs) -> (float, bool):
        weather = await getweather()
        rate = 200
        temperature_add = rate * abs(25 - weather.temperature) * 0.015
        weather_add = rate * 0.3 if weather.description.lower == 'rain' else 0
        wind_add = weather.wind_speed * rate * 0.001
        return rate + temperature_add + weather_add + wind_add, False

    async def create_order(self, chat_id, flower_id, number, delivery_price, address):
        db = FlowerDatabase()
        db.create_order(chat_id, flower_id, number, delivery_price, address)
        db.delete_message_buffer(chat_id)
        db.close()
        return "Order created successfully", True
        #return "Order added successfully. Delivery price is " + str(delivery_price), True


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_flowers_name_and_count",
            "description": "Get flowers name and count of each flower. Call this whenever you need to know what flowers are available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },

    },
    {
        "type": "function",
        "function": {
            "name": "calculate_delivery_cost",
            "description": "Calculate delivery cost for order. Call this whenever you need to know how much delivery cost after all order dateils. Delivery is available only in Lviv from 8:00 to 22:00, cancel other order",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },

    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create order. Use it only when you have all arguments about order, if not discover it. This function need all arguments, so use it",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "chat_id": {
                            "type": "string",
                            "description": "The customer chat ID."
                        },
                        "flower_id": {
                            "type": "string",
                            "description": "The flower ID."
                        },
                        "number": {
                            "type": "integer",
                            "description": "The number of flowers."
                        },
                        "delivery_price": {
                            "type": "number",
                            "description": "The delivery price."
                        },
                        "address": {
                            "type": "string",
                            "description": "The address where the order will be placed."
                        }
                    },
                    "required": ["chat_id", "flower_id", "number", "delivery_price", "address"],
                    "additionalProperties": False
                },

    },
    }
]


class FlowerAI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.model = "gpt-4o-mini"

    async def client_conversation(self, chat_id, msg, history="", additional_messages=None, final_answer=False):
        if additional_messages is None:
            additional_messages = []
        prompt = f"""
    Chat ID: {chat_id} - Use it necessarily for order tools to distinguish users.    
    
    Respond to the users current message:

    Chat history:
    {history}

    CURRENT QUESTION: 
    {msg}
    """
        messages = [
            {"role": "system",
             "content": f"You are a flower shop assistant. Answer only questions about purchases or greetings, ignore all others. Always check assistent answers, if you have tool response already, never call tool again and give finnaly response for the user. Now is "
             # f"{datetime.datetime.now().strftime('%I:%M%p on %B %d, %Y')}."
                        "17:30 10/05/2026 "
                        f"Use algorithm with user Greeting -> Details -> Delivery Details -> Create Order", },
            {"role": "user", "content": prompt}
        ]
        if additional_messages:
            messages.extend(additional_messages)
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=0.5,
            messages=messages,
            tools=tools if not final_answer else None,
        )
        response = completion.choices[0].message.content
        if 'tool_calls' in completion.choices[0].finish_reason:
            function_call = completion.choices[0].message.tool_calls
            args = json.loads(function_call[0].function.arguments)
            tool_func = Tools().__getattribute__(function_call[0].function.name)
            tool_response, final = await tool_func(**args)

            tool_message = [
                {"role": "assistant", "content": f"Tool '{function_call[0].function.name}' response: {tool_response}"}]
            tool_message.extend(additional_messages)
            return await self.client_conversation(chat_id, msg, history, tool_message, final)

        return response


if __name__ == '__main__':
    import dotenv
    import asyncio
    dotenv.load_dotenv()
    ai = FlowerAI()
    user_input = "Create order 5 roses on Patona 12 str"
    response = asyncio.run(ai.client_conversation(123, user_input))
    print(response)
