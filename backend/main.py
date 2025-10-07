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
    post_type: str  # "linkedin" or "instagram"
    generate_image: bool = True

@app.post("/generate-post")
async def generate_post(request: PostRequest):
    try:
        # Select prompt based on post type
        if request.post_type == "linkedin":
            post_prompt = f"""Create a professional LinkedIn post for {request.company_name} about: {request.event}
            
            Professional Requirements:
            - Write in a polished, executive-level tone
            - Use industry-specific terminology and insights
            - Include strategic emojis for engagement (but keep it professional)
            - Add relevant professional hashtags (10-15)
            - Format with proper spacing and line breaks for readability
            - Keep it concise but impactful (150-300 words)
            - Include a strong call-to-action
            - Make it feel authentic and human-written
            - Focus on value, impact, and thought leadership
            - Include data, insights, or industry trends when relevant
            - Use professional language that builds credibility
            - Structure with clear value proposition
            - End with engagement-driving question or CTA
            
            Tone: Professional, authoritative, insightful, and engaging"""
        else:
            post_prompt = f"""Create a viral Instagram carousel caption for {request.company_name} about: {request.event}
            
            Style Requirements (Youth-Centric & Content-Rich):
            - Use Gen Z language, slang, and trendy expressions (no cap, periodt, slay, etc.)
            - Make it highly engaging and shareable with emotional hooks
            - Include relatable scenarios and personal touches
            - Use current social media trends and memes
            - Add interactive elements (questions, polls, etc.)
            - Use power words and emotional triggers
            - Make it feel authentic and personal, like a friend sharing advice
            - Include storytelling elements and personal experiences
            
            Content Structure:
            1. Hook: Start with a relatable question or statement that grabs attention
            2. Story: Share a personal experience or relatable scenario
            3. Value: Provide actionable insights or tips
            4. Engagement: End with a question or call-to-action
            
            Format Requirements:
            - Use strategic line breaks for readability
            - Include relevant emojis (but not excessive)
            - Add 20-25 trending hashtags
            - Keep it conversational and authentic
            - Use current slang and expressions
            - Make it feel like a friend sharing advice
            - Include emotional elements and personal touches
            - Maximum 1000 characters
            
            Tone: Casual, authentic, relatable, engaging, and youth-focused"""

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
            # Generate carousel images
            image_prompts = [
                f"Create a professional title card for {request.event} with modern design, {request.company_name} branding, and attention-grabbing visuals. Use Instagram-optimized layout (1080x1080).",
                f"Create an infographic-style image showing the main points or steps about {request.event}. Use modern design, clear typography, and visually appealing layout. Make it part of a cohesive carousel series.",
                f"Create a summary slide for {request.event} with {request.company_name}'s branding, including a strong call-to-action. Match the style of previous slides for visual consistency."
            ]
            
            all_images = []
            all_mime_types = []
            
            for prompt in image_prompts:
                image_response = client.models.generate_content(
                    model=model,
                    contents=[prompt],
                )
                
                for part in image_response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        all_images.append(part.inline_data.data)
                        all_mime_types.append(part.inline_data.mime_type)
                        break

            if all_images:
                return {
                    "post": post_text,
                    "images": [
                        {
                            "data": img_data,
                            "mime_type": mime_type
                        } for img_data, mime_type in zip(all_images, all_mime_types)
                    ]
                }

        # Return just the post if no image was generated or requested
        return {"post": post_text}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}