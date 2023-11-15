from openai import OpenAI
import os


def test_openai_connection():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    #client = OpenAI()

    try:
        completion = client.chat.completions.create(
        # model="gpt-3.5-turbo",  
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "How long does it take to fly from scottsdale to denver?"}
        ]
        )

        print(completion.choices[0].message)
    except Exception as e:
        print(f"An error occurred: {e}")
    


if __name__ == "__main__":
    test_openai_connection()

