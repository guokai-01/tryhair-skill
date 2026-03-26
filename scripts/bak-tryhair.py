#!/usr/bin/env python3
"""
tryhair OpenClaw Skill script - supports hairstyle try-on and face shape analysis
"""

import os
import sys
import json
import base64
import argparse
import requests
import datetime
from pathlib import Path

TRYHAIR_API = os.environ.get('OPENCLAW_TRYHAIR_API', 'https://tryhair.ai/api/tryhair')
FACESHAPE_API = os.environ.get('OPENCLAW_FACESHAPE_API', 'https://tryhair.ai/api/facial_analysis')

def main():
    parser = argparse.ArgumentParser(description='AI Hairstyle & FaceShape Tool for OpenClaw')
    parser.add_argument('--action', default='tryhair', choices=['tryhair', 'faceshape'],
                        help='Action to perform: tryhair or faceshape')
    parser.add_argument('--image', required=True, help='Path to the image (face photo)')
    parser.add_argument('--style', help='Hairstyle description (required for tryhair action)')
    parser.add_argument('--uid', required=True, help='Userid from https://tryhair.ai')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.image):
        print(json.dumps({
            'success': False,
            'error': f'Image file does not exist: {args.image}'
        }))
        sys.exit(1)

    if args.action == 'tryhair':
        if not args.style:
            print(json.dumps({
                'success': False,
                'error': 'Missing --style parameter for tryhair action'
            }))
            sys.exit(1)
        _handle_tryhair(args)
    elif args.action == 'faceshape':
        _handle_faceshape(args)

last_request = {}
def is_duplicate(uid, style, window=30):
    key = f"{uid}:{style}"
    now = time.time()

    expired_keys = [
        k for k, t in last_request.items()
        if now - t > window
    ]
    for k in expired_keys:
        del last_request[k]

    if key in last_request:
        print(f"[DUPLICATE BLOCKED] {key}")
        return True

    last_request[key] = now
    return False

def _handle_tryhair(args):
    if is_duplicate(args.uid, args.style):
        print(json.dumps({
            'success': False,
            'error': 'Duplicate request ignored (client-side)'
        }))
        sys.exit(0)

    with open(args.image, 'rb') as f:
        files = {'facefile': f}
        data = {
            'hairstyle': args.style,
            'uid': args.uid
        }
        
        try:
            response = requests.post(
                TRYHAIR_API,
                files=files,
                data=data,
                timeout=180
            )

            print(f"Status Code: {response.status_code}", file=sys.stderr)
            print(f"Response Headers: {response.headers}", file=sys.stderr)
            print(f"Response Text: {response.text[:500]}", file=sys.stderr)
            
            result = response.json()
            _process_tryhair_response(result)
        except Exception as e:
            _error_exit(f'Request error: {str(e)}')

def _handle_faceshape(args):
    with open(args.image, 'rb') as f:
        files = {'facefile': f}
        data = {'uid': args.uid}

        try:
            response = requests.post(
                FACESHAPE_API,
                files=files,
                data=data,
                timeout=120
            )
            result = response.json()
            _process_faceshape_response(result)
        except Exception as e:
            _error_exit(f'Request error: {str(e)}')

def _process_tryhair_response(result):

    if result.get('status') == 'need_purchase':
        output = {
            'success': False,
            'need_purchase': True,
            'message': f"⚠️ {result.get('message')}\n\n[Upgrade Now]({result.get('redirect_url')})",
            'redirect_url': result['redirect_url'],
            'action': result.get('action', 'purchase')
        }

        if result.get('plans'):
            output['plans'] = result['plans']

        print(json.dumps(output))
        sys.exit(0)

    if result.get('status') == 'error':
        _error_exit(result.get('message', 'Unknown error'), result.get('code'))

    if result.get('status') == 'success':
        data = result['data']

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_style = data['hairstyle'].replace(" ", "_").replace("/", "_")

        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"output_{safe_style}_{timestamp}.jpg"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(data['image_base64']))

        style = data['hairstyle']
        credits = data['remaining_credits']

        message_lines = [
            f"✨ Your {style} hairstyle is ready!",
            "",
            "💇 Take a look above 👆",
            "",
            f"Credits remaining: {credits}",
            "",
            "Want to try another style?",
            '👉 "try shag"',
            '👉 "try shorter hair"',
        ]

        print(json.dumps({
            'success': True,
            'image_path': filepath,
            'message': "\n".join(message_lines),
            'style': style,
            'remaining_credits': credits
        }))

        sys.exit(0)

    _error_exit('Unexpected response format')

def _process_faceshape_response(result):
    if result.get('status') == 'need_signup':
        _error_exit(
            f"⚠️ {result.get('message')}\n\nPlease register at [tryhair.ai]({result.get('redirect_url', 'https://tryhair.ai')})",
            'USER_NOT_FOUND'
        )

    if result.get('status') == 'need_purchase':
        _error_exit(
            f"⚠️ {result.get('message')}\n\n[Upgrade Now]({result.get('redirect_url', 'https://tryhair.ai')})",
            'INSUFFICIENT_CREDITS'
        )

    if result.get('status') == 'error':
        _error_exit(result.get('message', 'Unknown error'), result.get('code'))

    analysis = result.get("analysis", {})
    ai = result.get("ai_recommendation", {})

    face_shape = analysis.get("Face Shape", "")
    face_ratio = analysis.get("Face Width : Cheek Width : Jaw Width : Face Length", "")
    five_eye = analysis.get("Right Eye Width : Inner Eye Width : Left Eye Width", "")
    three_court = analysis.get("Upper Face : Middle Face : Lower Face", "")

    if face_shape:
        face_shape = face_shape.replace("face shape", "")
        face_shape = face_shape.replace("You are likely", "").strip()
        face_shape = face_shape.replace(" ,", ",")
        face_shape = f"Likely: {face_shape}"


    output_lines = [
        "✨ Your Face Analysis",
        "",
        "Face Shape",
        face_shape,
    ]

    if isinstance(ai, dict) and ai.get("analysis"):
        summary = ai.get("analysis", "").strip()
        if summary:
            summary = summary.split(".")[0].strip() + "."
            output_lines.append(f"→ {summary}")

    output_lines += [
        "",
        "Proportions",
        f"• Face Ratio: {face_ratio}",
        f"• Eye Balance: {five_eye}",
        f"• Vertical Balance: {three_court}",
    ]


    if isinstance(ai, dict):
        design = ai.get("design", "")
        hairstyles = ai.get("hairstyles", [])

        output_lines += [
            "",
            "💡 Your Personalized Style Guide",
        ]

        if design:
            output_lines += [
                "",
                "Design Strategy",
                design
            ]

        if hairstyles:
            output_lines += [
                "",
                "🔥 Recommended Hairstyles (Tap to Try)"
            ]
            for i, h in enumerate(hairstyles, 1):
                name = h.get("name", "")
                desc = h.get("description", "")

                if name:
                    output_lines.append(f"{i:02d}. {name}")

                    if desc:
                        output_lines.append(f"   {desc}")

                    output_lines.append(f"   🔄 Try this look → {name}")

                    output_lines.append("") 
           

    output_lines += [
       "",
        "✨ Want to try one?",
        'Just say: "try this" or "try [style name]" 💇'
    ]

    formatted_text = "\n".join(output_lines)

    print(json.dumps({
        'success': True,
        'formatted': formatted_text,
        'data': result,
        'message': "Face shape analysis completed."
    }))

    sys.exit(0)

def _error_exit(error_msg, code=None):
    out = {'success': False, 'error': error_msg}
    if code:
        out['code'] = code
    print(json.dumps(out))
    sys.exit(1)
       
if __name__ == '__main__':
    main()

