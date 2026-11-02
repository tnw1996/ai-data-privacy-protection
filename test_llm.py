import ollama
response = ollama.chat(
    model="llama3.2:3b",
    messages=[
        {
            "role": "user",
            "content": "Explain data anonymisation in three simple points."
        }
    ]
)

print("\n========== LLM RESPONSE ==========")
print(response["message"]["content"])
print("=================================")
