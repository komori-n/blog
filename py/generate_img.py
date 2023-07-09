import shutil
import openai
import os
import sys
import requests
from blog import Post

openai.api_key = os.getenv("OPENAI_KEY")


def generate_text_prompt(title: str, content: str) -> str:
    prompt = (
        f"# The following is the beginning of a technical blog post titled '{title}.'"
    )

    prompt += "\n\n--- begin of content ---\n"
    prompt += content[:500]
    prompt += "\n--- end of content ---\n\n"
    prompt += "# Please describe a short English prompt that describes"
    prompt += "the most likely header image of the post\n"

    return prompt


def save_image(image_url: str, filepath: str):
    image_res = requests.get(image_url, stream=True)
    if image_res.status_code == 200:
        with open(filepath, "wb") as f:
            shutil.copyfileobj(image_res.raw, f)


post = Post(sys.argv[1])
response = openai.Completion.create(
    model="text-davinci-003",
    prompt=generate_text_prompt(post.title, post.content),
    max_tokens=100,
    temperature=0.1,
)
image_prompt = response["choices"][0]["text"].strip()
print("image prompt:", image_prompt)
response = openai.Image.create(prompt=image_prompt, n=1, size="512x512")
image_url = response["data"][0]["url"]
save_image(image_url, "generated.png")
