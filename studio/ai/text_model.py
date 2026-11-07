# pip install torch transformers accelerate
import json, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
_tok = _model = None

def make_storyboard(prompt, style, n):
    global _tok, _model
    if _model is None:
        _tok = AutoTokenizer.from_pretrained(_NAME)
        _model = AutoModelForCausalLM.from_pretrained(_NAME, torch_dtype="auto", device_map="auto")
    msgs = [{"role": "system", "content":
             "Return ONLY a JSON list. Each item has keys: title, description, camera_movement, "
             "lighting, image_prompt, video_prompt."},
            {"role": "user", "content": f"Style: {style}. Create {n} scenes for: {prompt}"}]
    text = _tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = _tok(text, return_tensors="pt").to(_model.device)
    out = _model.generate(**ids, max_new_tokens=1500, do_sample=True, temperature=0.7)
    raw = _tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True)
    return json.loads(raw[raw.index("["): raw.rindex("]") + 1])[:n]