from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_KEY")
print(f"Key found: {bool(api_key)}")

if api_key:
    client = genai.Client(api_key=api_key)
    try:
        model_name = 'gemini-2.0-flash-exp-image-generation'
        print(f"Attempting generation with '{model_name}'...")
        response = client.models.generate_images(
            model=model_name,
            prompt='A detailed drawing of a futuristic city',
            config=types.GenerateImagesConfig(
                number_of_images=1,
            )
        )
        print("Success!")
        if response.generated_images:
            print(f"Generated {len(response.generated_images)} image(s).")
            # Verify we have bytes
            img_bytes = response.generated_images[0].image.image_bytes
            print(f"Image size: {len(img_bytes)} bytes")
        else:
            print("No images returned.")
            
    except Exception as e:
        print(f"Error: {e}")
