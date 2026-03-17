#!/usr/bin/env python3
"""Tensorslab Image Generate - CLI for Star Office UI background generation.

Calls Tensorslab API to generate images.
Compatible with gemini_image_generate.py interface.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the current directory to sys.path so we can import tensorslab_image
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tensorslab_image import generate_image, wait_and_download
except ImportError:
    print("ERROR: tensorslab_image not found", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate image via Tensorslab API")
    parser.add_argument("--prompt", required=True, help="Generation prompt")
    parser.add_argument("--model", default="seedreamv5", help="Model name")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    parser.add_argument("--cleanup", action="store_true", help="(ignored, kept for compat)")
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio hint (e.g. 16:9)")
    parser.add_argument("--reference-image", default="", help="Reference image path")
    args = parser.parse_args()

    # Resolve API key
    api_key = os.environ.get("TENSORSLAB_API_KEY", "").strip()
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: TENSORSLAB_API_KEY or GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Resolve model
    model = os.environ.get("TENSORSLAB_MODEL", "").strip() or args.model.strip()
    if not model:
        model = "seedreamv5"

    # Ensure output directory
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = None
    if args.reference_image and os.path.exists(args.reference_image):
        sources = [args.reference_image]

    # Map aspect ratio to resolution if needed (Tensorslab accepts 16:9)
    resolution = args.aspect_ratio if args.aspect_ratio else "16:9"

    try:
        task_id = generate_image(
            prompt=args.prompt,
            model=model,
            resolution=resolution,
            source_images=sources,
            api_key=api_key
        )
        
        # We output to the out_dir specified
        downloaded = wait_and_download(
            task_id=task_id,
            api_key=api_key,
            output_dir=out_dir
        )
        
        if not downloaded:
            print("ERROR: No image generated.", file=sys.stderr)
            sys.exit(1)
            
        # Output result as JSON (backend reads the last line)
        result = {"files": downloaded}
        print(json.dumps(result))
        
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
