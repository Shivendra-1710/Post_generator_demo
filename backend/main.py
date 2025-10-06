from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Initialize the client with API key
client = genai.Client(api_key=api_key)

# Initialize models
try:
    # Configure the model
    model = "gemini-2.5-flash-image"
except Exception as e:
    print(f"Error initializing models: {str(e)}")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PostRequest(BaseModel):
    company_name: str
    event: str
    generate_image: bool = True

@app.post("/generate-post")
async def generate_post(request: PostRequest):
    try:
        # Generate the text post
        post_prompt = f"""Create a professional LinkedIn post about:
        Company: {request.company_name}
        Event: {request.event}"""

        response = client.models.generate_content(
            model=model,
            contents=[post_prompt],
        )
        
        post_text = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                post_text = part.text
                break
            
        if not post_text:
            raise HTTPException(status_code=500, detail="Failed to generate post text")

        # If image generation is requested
        if request.generate_image:
            # Generate an image
            image_prompt = f"Create a professional image for {request.company_name} about {request.event}"
            
            image_response = client.models.generate_content(
                model=model,
                contents=[image_prompt],
            )

            # Process image response
            image_data = None
            image_mime_type = None
            for part in image_response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    image_mime_type = part.inline_data.mime_type
                    break

            if image_data:
                return {
                    "post": post_text,
                    "image_data": image_data,
                    "mime_type": image_mime_type
                }

        # Return just the post if no image was generated or requested
        return {"post": post_text}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}