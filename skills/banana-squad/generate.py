#!/usr/bin/env python3
"""
Banana Squad — Gemini Image Generator
Calls gemini-3-pro-image-preview and saves output PNG.

Usage:
  python3 generate.py --prompt "..." --output /path/to/output.png
  python3 generate.py --prompt "..." --aspect-ratio 16:9 --size 2K --output /path/to/output.png
"""

import argparse
import os
import sys

def load_api_key():
    """Load GOOGLE_API_KEY from claudeclaw .env, fall back to GEMINI_API_KEY env var."""
    # Try claudeclaw .env first
    env_path = os.path.expanduser("/Users/alex/dev/claudeclaw/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GOOGLE_API_KEY=") and not line.startswith("#"):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        return key

    # Fall back to environment variable
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key:
        return key

    return None


def generate_image(prompt: str, aspect_ratio: str = "16:9", image_size: str = "2K", output_path: str = "output.png"):
    """Generate an image using Gemini 3 Pro Image API."""

    api_key = load_api_key()
    if not api_key:
        print("ERROR: No API key found.")
        print("  Set GEMINI_API_KEY in environment, or add GOOGLE_API_KEY to /Users/alex/dev/claudeclaw/.env")
        sys.exit(1)

    print(f"API key loaded: {api_key[:12]}...")
    print(f"Model:         gemini-3-pro-image-preview")
    print(f"Aspect ratio:  {aspect_ratio}")
    print(f"Resolution:    {image_size}")
    print(f"Output:        {output_path}")
    print(f"Prompt:        {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    print()
    print("Generating... (this may take 20-60 seconds)")

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("ERROR: google-genai not installed. Run: pip3 install google-genai Pillow --break-system-packages")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
            ),
        )

        saved = False
        for part in response.parts:
            if part.text:
                print(f"Model note: {part.text}")
            elif part.inline_data:
                # Ensure output directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                image = part.as_image()
                image.save(output_path)
                print(f"\nSUCCESS: Saved to {output_path}")
                saved = True

        if not saved:
            print("WARNING: No image in response. The model may have declined the prompt.")
            sys.exit(1)

    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            print("\nERROR: 429 RESOURCE_EXHAUSTED")
            print("  Your API key is on the free tier — gemini-3-pro-image requires a paid plan.")
            print("  Upgrade at: https://aistudio.google.com/apikey")
            print("  Then add the new key to /Users/alex/dev/claudeclaw/.env as GOOGLE_API_KEY=...")
            sys.exit(2)
        elif "400" in err and "paid" in err.lower():
            print("\nERROR: This model requires a paid Gemini API plan.")
            print("  Upgrade at: https://aistudio.google.com/apikey")
            sys.exit(2)
        else:
            print(f"\nERROR: {err}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Banana Squad — Gemini Image Generator")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--aspect-ratio", "-r", default="16:9",
                        choices=["1:1", "16:9", "9:16", "3:2", "2:3", "4:3", "3:4", "4:5", "5:4", "21:9"],
                        help="Image aspect ratio (default: 16:9)")
    parser.add_argument("--size", "-s", default="2K",
                        choices=["1K", "2K", "4K"],
                        help="Image resolution (default: 2K)")
    parser.add_argument("--output", "-o", default="output.png",
                        help="Output file path (default: output.png)")
    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        aspect_ratio=args.aspect_ratio,
        image_size=args.size,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
