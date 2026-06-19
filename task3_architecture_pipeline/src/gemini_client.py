import os
import json
import logging

def generate_plan_with_gemini(requirements: str, verbosity: int = 1):
    """Try to call Gemini (Google Generative AI) to generate a JSON plan.
    Returns a dict if JSON parsed, a string if raw text, or None on failure.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    prompt = (
        "Convert the following high-level requirement into a JSON object with keys:"
        " title, modules (list of {name,purpose,tech}), schemas (mapping of entity->fields),"
        " pseudocode (mapping of flow->steps), and notes. Return only valid JSON.\n\n"
        f"Requirement:\n{requirements}\n\nBe concise and return only JSON."
    )

    # Try multiple SDK import styles to be robust in different environments
    try:
        # Preferred: google.generativeai
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                resp = model.generate_content(prompt)
                text = resp.text
            except Exception:
                resp = genai.generate_text(model="models/text-bison-001", input=prompt)
                text = getattr(resp, 'text', None) or str(resp)
        except Exception:
            # Alternative import path
            try:
                from google import generativeai as genai
                genai.configure(api_key=api_key)
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    resp = model.generate_content(prompt)
                    text = resp.text
                except Exception:
                    resp = genai.generate_text(model="models/text-bison-001", input=prompt)
                    text = getattr(resp, 'text', None) or str(resp)
            except Exception as e:
                logging.exception('Gemini SDK call failed')
                return None

        # Try parsing JSON directly
        try:
            return json.loads(text)
        except Exception:
            # Attempt to extract JSON substring
            import re
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    return text
            return text

    except Exception as e:
        logging.exception('Unexpected error calling Gemini')
        return None
