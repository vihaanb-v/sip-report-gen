import base64
import requests
import os
from openai import OpenAI

client = OpenAI()

def encode_image(image_path_folder):
    encoded_images = []
    for i in range(len(image_path_folder)):
      with open(image_path_folder[i], "rb") as image_file:
          encoded_images[i] = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_images

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)

if __name__ == "__main__":
    image_path_list = []
    for i in range()