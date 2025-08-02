import os
import openai

openai.api_key = os.getenv("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")

def call_openai(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]
