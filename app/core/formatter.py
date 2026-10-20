from app.schemas import Verdict

def format_whatsapp(verdict: Verdict) -> str:
    icon_map = {"DANGER": "🚨", "CAUTION": "⚠️", "SAFE": "✅", "UNSURE": "❓"}
    icon = icon_map.get(verdict.level, "❓")
    
    # Verdict Header
    text = f"{icon} *{verdict.level}* (Score: {verdict.score})\n\n"
    
    # One reason
    if verdict.reasons:
        text += f"*Reason:* {verdict.reasons[0]}\n"
        
    # One action
    text += f"*Action:* {verdict.advice}\n\n"
    
    # Disclaimer
    if verdict.level in ("SAFE", "UNSURE"):
        text += "_Not on the list does not mean guaranteed safe._"
        
    # Keep under 600 chars
    return text[:600]