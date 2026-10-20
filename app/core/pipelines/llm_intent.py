import hashlib
import json
from openai import OpenAI, APITimeoutError, APIConnectionError
from app.config import settings

# In-memory cache to save cost during the demo
_llm_cache = {}

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_llm_intent(text: str) -> tuple[int, dict]:
    text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    if text_hash in _llm_cache:
        return _llm_cache[text_hash]["score"], _llm_cache[text_hash]["data"]
        
    prompt = f"""
    Analyze the following message for scams. 
    Respond ONLY with strict JSON matching this exact structure:
    {{"verdict": "SAFE|CAUTION|DANGER", "scam_type": "impersonation|job|investment|parcel|other", "reason_ms": "...", "reason_en": "...", "confidence": 0.0}}
    
    Message: "{text}"
    """
    
    try:
        # Set a 6-second timeout as required
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Or gpt-4o-mini for speed and cost
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=6.0 
        )
        
        result_text = response.choices[0].message.content
        data = json.loads(result_text)
        
        # Translate LLM verdict to a numerical score
        score_map = {"DANGER": 90, "CAUTION": 60, "SAFE": 10}
        score = score_map.get(data.get("verdict", "CAUTION"), 0)
        
        # Weight by confidence if provided
        confidence = float(data.get("confidence", 1.0))
        final_llm_score = int(score * confidence)
        
        _llm_cache[text_hash] = {"score": final_llm_score, "data": data}
        return final_llm_score, data
        
    except (APITimeoutError, APIConnectionError, json.JSONDecodeError):
        # On failure, fall back to the rule score alone
        return 0, {}