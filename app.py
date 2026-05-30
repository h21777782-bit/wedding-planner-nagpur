import streamlit as st
import openai
import anthropic
import base64
import json
import random
import concurrent.futures
import requests as http_requests
import datetime
import calendar as cal_lib
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

st.set_page_config(
    page_title="Wedding Carousel Generator · Nagpur",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Lato:wght@300;400;700&display=swap');

.stApp { background: linear-gradient(135deg, #fdf6f0 0%, #fef9f5 50%, #f9f0f5 100%); }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; }

.brand {
    text-align: center;
    background: linear-gradient(135deg, #8B0000, #C2185B, #880E4F);
    border-radius: 20px; padding: 1.8rem 1rem; margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(139,0,0,0.25);
}
.brand h1 { font-family:'Cormorant Garamond',serif; font-size:2.5rem; color:#fff; margin:0; }
.brand p  { font-family:'Lato',sans-serif; font-size:0.85rem; color:rgba(255,255,255,0.75); letter-spacing:4px; margin:0.3rem 0 0; }

.card {
    background: rgba(255,255,255,0.9); border-radius: 14px; padding: 1.4rem;
    margin-bottom: 1rem; box-shadow: 0 2px 16px rgba(139,0,0,0.07);
    border: 1px solid rgba(194,24,91,0.1);
}
.label {
    font-family:'Lato',sans-serif; font-size:0.72rem; font-weight:700;
    text-transform:uppercase; letter-spacing:2px; color:#C2185B; margin-bottom:0.5rem;
}
.free-badge {
    display:inline-block; background:#22c55e; color:white;
    font-family:Lato,sans-serif; font-size:0.65rem; font-weight:700;
    padding:2px 8px; border-radius:20px; margin-left:6px; letter-spacing:1px;
}
.provider-card {
    border:2px solid rgba(194,24,91,0.15); border-radius:12px; padding:1rem;
    margin-bottom:0.6rem; cursor:pointer; transition:all 0.2s;
    background:white;
}
.provider-card.active { border-color:#C2185B; background:rgba(194,24,91,0.04); }

.stButton > button {
    width:100%; background: linear-gradient(135deg, #8B0000, #C2185B);
    color:white; border:none; border-radius:50px; padding:0.8rem 2rem;
    font-family:'Lato',sans-serif; font-size:1rem; font-weight:700;
    letter-spacing:1.5px; text-transform:uppercase;
    box-shadow: 0 4px 20px rgba(194,24,91,0.35); transition: all 0.3s;
}
.stButton > button:hover { transform:translateY(-2px); box-shadow: 0 8px 28px rgba(194,24,91,0.5); }

.slide-preview {
    background:white; border-radius:16px; padding:1.2rem;
    border:2px solid rgba(194,24,91,0.15); margin-bottom:0.8rem;
}
.slide-num   { font-family:'Lato',sans-serif; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:2px; color:#C2185B; margin-bottom:0.3rem; }
.slide-title { font-family:'Cormorant Garamond',serif; font-size:1.25rem; font-weight:600; color:#2a2a2a; margin-bottom:0.3rem; }
.slide-body  { font-family:'Lato',sans-serif; font-size:0.88rem; color:#555; line-height:1.6; }
.slide-cta   { font-family:'Lato',sans-serif; font-size:0.85rem; font-weight:700; color:#C2185B; margin-top:0.5rem; }

.stDownloadButton > button {
    width:100%; background:transparent; border:2px solid #C2185B; color:#C2185B;
    border-radius:50px; font-family:'Lato',sans-serif; font-weight:700;
    padding:0.45rem 1rem; transition:all 0.2s;
}
.stDownloadButton > button:hover { background:#C2185B; color:white; }

.insta-box {
    background: linear-gradient(135deg, #f9f0f5, #fdf6f0);
    border-radius:16px; padding:1.5rem; border:2px solid rgba(194,24,91,0.2); margin-top:1.5rem;
}
.insta-title { font-family:'Cormorant Garamond',serif; font-size:1.3rem; font-weight:600; color:#8B0000; margin-bottom:1rem; }
.help-tip {
    font-family:'Lato',sans-serif; font-size:0.78rem; color:#888;
    background:#fff; border-radius:8px; padding:0.7rem 1rem;
    border-left:3px solid #C2185B; margin-bottom:1rem; line-height:1.6;
}
.powered-by {
    font-family:'Lato',sans-serif; font-size:0.72rem; color:#aaa;
    text-align:center; margin-top:0.5rem; letter-spacing:1px;
}

/* ── Monthly Planner ── */
.planner-header {
    font-family:'Cormorant Garamond',serif; font-size:2rem; font-weight:600;
    color:#8B0000; text-align:center; margin:2rem 0 1.5rem;
}
.topic-chip {
    display:inline-flex; align-items:center; gap:8px;
    background:rgba(194,24,91,0.08); border:1px solid rgba(194,24,91,0.2);
    border-radius:50px; padding:5px 14px; margin:4px;
    font-family:Lato,sans-serif; font-size:0.82rem; color:#8B0000;
}
.sched-row {
    display:flex; align-items:center; gap:12px;
    background:white; border-radius:10px; padding:0.7rem 1rem;
    margin-bottom:6px; border:1px solid rgba(194,24,91,0.1);
    font-family:Lato,sans-serif; font-size:0.85rem;
}
.sched-date { color:#8B0000; font-weight:700; min-width:90px; }
.sched-time { color:#C2185B; min-width:80px; font-size:0.78rem; }
.sched-topic { color:#444; flex:1; }
.time-9am  { background:#fff9e6; color:#b45309; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.time-6pm  { background:#f0fdf4; color:#15803d; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }
.time-9pm  { background:#f0f4ff; color:#3730a3; border-radius:4px; padding:2px 8px; font-size:0.72rem; font-weight:700; }

/* Calendar */
.cal-wrap { background:white; border-radius:16px; padding:1.2rem; border:1px solid rgba(194,24,91,0.12); }
.cal-month-name { font-family:'Cormorant Garamond',serif; font-size:1.2rem; font-weight:600; color:#8B0000; text-align:center; margin-bottom:0.8rem; }
.cal-grid { display:grid; grid-template-columns:repeat(7,1fr); gap:4px; }
.cal-dow  { font-family:Lato,sans-serif; font-size:0.68rem; font-weight:700; text-align:center; color:#aaa; text-transform:uppercase; padding:4px 0; }
.cal-cell { border-radius:8px; padding:4px 2px; text-align:center; min-height:42px; background:#fafafa; }
.cal-cell.has-posts { background:rgba(194,24,91,0.06); }
.cal-cell.empty { background:transparent; }
.cal-day  { font-family:Lato,sans-serif; font-size:0.78rem; color:#555; display:block; }
.cal-dots { display:flex; justify-content:center; gap:3px; margin-top:2px; }
.dot-9am  { width:7px; height:7px; border-radius:50%; background:#f59e0b; display:inline-block; }
.dot-6pm  { width:7px; height:7px; border-radius:50%; background:#22c55e; display:inline-block; }
.dot-9pm  { width:7px; height:7px; border-radius:50%; background:#6366f1; display:inline-block; }
.cal-legend { display:flex; gap:16px; justify-content:center; margin-top:0.8rem; font-family:Lato,sans-serif; font-size:0.75rem; color:#666; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand">
    <h1>💍 WeddingEventPlanner Nagpur</h1>
    <p>CAROUSEL CONTENT GENERATOR</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# HELPERS — Text (Claude)
# ═══════════════════════════════════════════════════════════════════════

def generate_slides_content(claude_key: str, topic: str, num_slides: int, tone: str, platform: str) -> dict:
    tone_map = {
        "Elegant & Romantic": "sophisticated, romantic, luxurious",
        "Fun & Vibrant":       "lively, colorful, joyful, celebratory",
        "Warm & Emotional":    "heartfelt, touching, family-oriented",
    }
    client = anthropic.Anthropic(api_key=claude_key)
    prompt = f"""You are a social media content creator for WeddingEventPlanner Nagpur, a premium Indian wedding planning company.

Create a {num_slides}-slide carousel post for {platform} about: "{topic}"
Tone: {tone} ({tone_map.get(tone, '')})

Return a JSON object with:
- "slides": array of {num_slides} objects, each with:
  - "slide_number": int
  - "hook": attention-grabbing opening line (only slide 1, empty string otherwise) — e.g. "Did you know...?" or "The secret to..." or a bold statement
  - "title": short punchy heading (max 8 words)
  - "body": 2-3 engaging lines of content
  - "image_prompt": vivid visual description for AI image generation — focus ONLY on Indian wedding DECOR: floral arrangements, mandap, venue, table settings, lighting, flowers, fabric draping. NO people, NO humans, NO couples. Specific colors, textures, mood.
  - "cta": call-to-action line (only last slide, empty string otherwise) — e.g. "DM us to book your dream wedding 💍" or "Save this post for inspiration!"
- "caption": Instagram/Facebook caption with 3-4 emojis, starting with a strong hook line
- "hashtags": array of exactly 15 hashtag strings (no # symbol)

Return ONLY valid JSON, nothing else."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2200,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()
    # Strip markdown code block if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ═══════════════════════════════════════════════════════════════════════
# HELPERS — Image generation
# ═══════════════════════════════════════════════════════════════════════

def generate_image_together(together_key: str, prompt: str) -> bytes:
    """Together AI — FLUX.1-schnell-Free — 100% free, no cost per image."""
    full = (
        f"Ultra-realistic professional wedding photography: {prompt}. "
        "Luxurious Indian wedding decor, stunning floral arrangements, marigold and rose decorations, "
        "grand mandap setup, royal venue interior, elegant table settings, beautiful lighting, "
        "NO people, NO humans, NO faces, NO couples — only decor and venue, "
        "golden hour warm light, Canon EOS R5, 85mm f/1.4 lens, shallow depth of field, "
        "vibrant rich colors, no text, no watermarks, hyperrealistic 8K."
    )
    resp = http_requests.post(
        "https://api.together.xyz/v1/images/generations",
        headers={"Authorization": f"Bearer {together_key}", "Content-Type": "application/json"},
        json={"model": "black-forest-labs/FLUX.1-schnell-Free", "prompt": full,
              "width": 1024, "height": 1024, "steps": 4, "n": 1, "response_format": "b64_json"},
        timeout=120,
    )
    resp.raise_for_status()
    return base64.b64decode(resp.json()["data"][0]["b64_json"])


def generate_image_openai(openai_key: str, prompt: str, quality: str = "low") -> bytes:
    """OpenAI gpt-image-1. quality: low (~$0.011) | medium (~$0.042) | high (~$0.167)"""
    client = openai.OpenAI(api_key=openai_key)
    full = (
        f"Ultra-realistic professional wedding photography: {prompt}. "
        "Luxurious Indian wedding decor, stunning floral arrangements, marigold and rose decorations, "
        "grand mandap setup, royal venue interior, elegant table settings, beautiful lighting, "
        "NO people, NO humans, NO faces, NO couples — only decor and venue, "
        "golden hour warm light, Canon EOS R5, 85mm f/1.4 lens, shallow depth of field, "
        "vibrant rich colors, NO text, NO watermarks, NO illustration, hyperrealistic 8K."
    )
    resp = client.images.generate(
        model="gpt-image-1", prompt=full,
        size="1024x1024", quality=quality, n=1,
    )
    return base64.b64decode(resp.data[0].b64_json)


# ═══════════════════════════════════════════════════════════════════════
# HELPERS — Text overlay on image
# ═══════════════════════════════════════════════════════════════════════

INSTA_HANDLE = "@Eliteweddingplanner_nagpur"

def add_text_overlay(image_bytes: bytes, title: str, body: str, slide_num: int, total: int) -> bytes:
    img = Image.open(BytesIO(image_bytes)).convert("RGBA")
    W, H = img.size

    # Dark gradient — bottom 48%
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    grad_start = int(H * 0.46)
    for y in range(grad_start, H):
        alpha = int(225 * (y - grad_start) / (H - grad_start))
        ov_draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    def load_font(size, bold=False):
        candidates = (
            [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/calibrib.ttf",
                "C:/Windows/Fonts/seguisb.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            ] if bold else [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "C:/Windows/Fonts/segoeui.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            ]
        )
        for fp in candidates:
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
        try:
            return ImageFont.load_default(size=size)
        except Exception:
            return ImageFont.load_default()

    font_title  = load_font(76, bold=True)
    font_body   = load_font(40)
    font_badge  = load_font(32)
    font_handle = load_font(34, bold=True)

    pad, text_y = 60, int(H * 0.48)

    # Slide counter badge — top right
    draw.rounded_rectangle([(W - 130, 28), (W - 24, 72)], radius=20, fill=(0, 0, 0, 160))
    draw.text((W - 120, 32), f" {slide_num} / {total} ", font=font_badge, fill=(255, 255, 255, 230))

    # Title
    for line in textwrap.wrap(title, width=22):
        draw.text((pad, text_y), line, font=font_title, fill=(255, 255, 255, 255))
        text_y += 88
    text_y += 10

    # Body
    for line in textwrap.wrap(body, width=38)[:3]:
        draw.text((pad, text_y), line, font=font_body, fill=(235, 235, 235, 220))
        text_y += 52

    # Instagram handle — bottom RIGHT corner
    handle_bbox = draw.textbbox((0, 0), INSTA_HANDLE, font=font_handle)
    handle_w = handle_bbox[2] - handle_bbox[0]
    handle_x = W - handle_w - pad
    handle_y = H - 62
    draw.rounded_rectangle(
        [(handle_x - 16, handle_y - 8), (handle_x + handle_w + 16, handle_y + 42)],
        radius=20, fill=(0, 0, 0, 170),
    )
    draw.text((handle_x, handle_y), INSTA_HANDLE, font=font_handle, fill=(255, 255, 255, 240))

    buf = BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def generate_single_slide_image(provider: str, api_key_img: str,
                                 prompt: str, slide_num: int, total: int,
                                 title: str, body: str, quality: str = "low"):
    if provider == "together":
        raw = generate_image_together(api_key_img, prompt)
    else:
        raw = generate_image_openai(api_key_img, prompt, quality)
    return slide_num, add_text_overlay(raw, title, body, slide_num, total)


# ═══════════════════════════════════════════════════════════════════════
# HELPERS — Instagram
# ═══════════════════════════════════════════════════════════════════════

def upload_to_imgbb(imgbb_key: str, img_bytes: bytes) -> str:
    r = http_requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": imgbb_key, "image": base64.b64encode(img_bytes).decode()},
        timeout=30,
    )
    r.raise_for_status()
    d = r.json()
    if not d.get("success"):
        raise Exception(f"imgbb error: {d}")
    return d["data"]["url"]


def post_to_instagram(access_token, ig_user_id, image_urls, caption, scheduled_ts=None):
    base = "https://graph.facebook.com/v19.0"
    ids = []
    for url in image_urls:
        r = http_requests.post(f"{base}/{ig_user_id}/media",
                               data={"image_url": url, "is_carousel_item": "true", "access_token": access_token},
                               timeout=30)
        r.raise_for_status()
        ids.append(r.json()["id"])

    payload = {"media_type": "CAROUSEL", "children": ",".join(ids),
               "caption": caption, "access_token": access_token}
    if scheduled_ts:
        payload["scheduled_publish_time"] = str(scheduled_ts)
        payload["published"] = "false"

    r = http_requests.post(f"{base}/{ig_user_id}/media", data=payload, timeout=30)
    r.raise_for_status()
    carousel_id = r.json()["id"]

    if not scheduled_ts:
        r = http_requests.post(f"{base}/{ig_user_id}/media_publish",
                               data={"creation_id": carousel_id, "access_token": access_token},
                               timeout=30)
        r.raise_for_status()
        return r.json()
    return {"id": carousel_id, "scheduled": True}


# ═══════════════════════════════════════════════════════════════════════
# ── Load saved secrets (ek baar save, hamesha kaam) ──────────────────
def _s(key, fallback=""):
    """Read from secrets.toml if available, else return fallback."""
    try:
        return st.secrets.get(key, fallback) or fallback
    except Exception:
        return fallback

# ═══════════════════════════════════════════════════════════════════════
# UI LAYOUT
# ═══════════════════════════════════════════════════════════════════════
col_input, col_output = st.columns([1, 1.6], gap="large")

with col_input:

    # Claude API Key
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">🤖 Claude API Key <span style="font-size:0.65rem;color:#888;">(captions & content)</span></div>', unsafe_allow_html=True)
    claude_key = st.text_input("claude_key", type="password", placeholder="sk-ant-...", value=_s("CLAUDE_KEY"), label_visibility="collapsed")
    st.markdown('<div class="powered-by">Powered by Claude · Anthropic</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Image Provider
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">🎨 Image Generation Provider</div>', unsafe_allow_html=True)
    img_provider = st.radio(
        "provider",
        options=[
            "🆓  Together AI  (FLUX · Free API Key)",
            "💳  OpenAI gpt-image-1  (Best quality · Paid)",
        ],
        label_visibility="collapsed",
        key="img_provider_radio",
    )
    provider_key = "together" if "Together" in img_provider else "openai"

    if provider_key == "together":
        together_key = st.text_input("Together AI API Key", type="password", placeholder="...", value=_s("TOGETHER_KEY"), key="tog_key")
        img_quality = "low"
        st.markdown("""
        <div style='background:#f0fdf4;border-radius:8px;padding:0.7rem 1rem;
             font-family:Lato;font-size:0.79rem;color:#15803d;margin-top:0.5rem;line-height:1.7;'>
            ✅ <b>Bilkul Free!</b> FLUX.1-schnell model use hoga<br>
            👉 <b>together.ai</b> pe free account banao → API Key lo → bas!
        </div>
        """, unsafe_allow_html=True)
        openai_key = ""
    else:
        together_key = ""
        img_quality = "low"
        openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...", value=_s("OPENAI_KEY"), key="oai_key")
        img_quality = st.select_slider(
            "Image Quality",
            options=["low", "medium", "high"],
            value="low",
            key="img_quality",
        )
        cost_map = {"low": "~$0.011 (~₹0.93)", "medium": "~$0.042 (~₹3.5)", "high": "~$0.167 (~₹14)"}
        color_map = {"low": "#15803d", "medium": "#b45309", "high": "#dc2626"}
        st.markdown(f"""
        <div style='background:#f9fafb;border-radius:8px;padding:0.6rem 1rem;
             font-family:Lato;font-size:0.8rem;color:{color_map[img_quality]};margin-top:0.3rem;'>
            💰 <b>{img_quality.upper()}</b> quality — <b>{cost_map[img_quality]}</b> per image
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Platform
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">📱 Platform</div>', unsafe_allow_html=True)
    platform = st.selectbox("Platform", ["Instagram", "Facebook", "WhatsApp"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Tone
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">🎭 Tone</div>', unsafe_allow_html=True)
    tone = st.selectbox("Tone", ["Elegant & Romantic", "Fun & Vibrant", "Warm & Emotional"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Topic
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">✏️ Topic</div>', unsafe_allow_html=True)
    topic = st.text_area("topic", placeholder="e.g. Top 7 wedding decoration trends in Nagpur 2025…", height=100, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Slides
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">🗂️ Number of Slides</div>', unsafe_allow_html=True)
    num_slides = st.slider("slides", min_value=1, max_value=9, value=5, label_visibility="collapsed")
    st.markdown(f'<div style="text-align:center;font-family:Lato;color:#C2185B;font-weight:700;font-size:1.3rem;">{num_slides} slides</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    btn_slides = st.button("📝  Step 1 · Generate Slide Content", use_container_width=True)
    btn_images = st.button("🎨  Step 2 · Generate Carousel Images", use_container_width=True)

    # Instagram Credentials — always visible
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">📸 Instagram Credentials</div>', unsafe_allow_html=True)
    ig_token_left   = st.text_input("Access Token", type="password", placeholder="EAABs...",
                                     value=_s("IG_TOKEN"), key="ig_token_left")
    ig_uid_left     = st.text_input("Account ID", placeholder="17841400...",
                                     value=_s("IG_USER_ID"), key="ig_uid_left")
    imgbb_key_left  = st.text_input("imgbb Key", type="password", placeholder="abc123...",
                                     value=_s("IMGBB_KEY"), key="imgbb_key_left")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style='background:rgba(194,24,91,0.06);border-radius:12px;padding:1rem;margin-top:0.5rem;
         font-family:Lato;font-size:0.82rem;color:#666;line-height:1.8;'>
        <b style='color:#C2185B;'>How to use:</b><br>
        1️⃣ Topic daalo → Generate Content<br>
        2️⃣ Generate Images<br>
        3️⃣ Post / Schedule to Instagram 📸
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
with col_output:

    # STEP 1 — Claude generates all text
    if btn_slides:
        if not claude_key:
            st.error("Claude API Key daalo (sk-ant- se shuru hoti hai).")
        elif not topic.strip():
            st.error("Topic daalo pehle.")
        else:
            try:
                with st.spinner("🤖 Claude slides likh raha hai…"):
                    data = generate_slides_content(claude_key, topic.strip(), num_slides, tone, platform)
                st.session_state["slides_data"] = data
                st.session_state["images"] = {}
                st.success(f"✅ {num_slides} slides ready! Ab **Generate Carousel Images** click karo.")
            except anthropic.AuthenticationError:
                st.error("Invalid Claude API key.")
            except Exception as e:
                st.error(f"Error: {e}")

    # STEP 2 — Image generation
    if btn_images:
        img_api_key = together_key if provider_key == "together" else openai_key
        if "slides_data" not in st.session_state:
            st.error("Pehle Step 1 karo.")
        elif not img_api_key:
            st.error("Image provider ka API Key daalo.")
        else:
            slides = st.session_state["slides_data"]["slides"]
            images = {}
            progress = st.progress(0, text="Images generate ho rahi hain…")
            provider_label = "Together AI FLUX (free)" if provider_key == "together" else "DALL-E 3"
            try:
                max_w = 2 if provider_key == "together" else 4
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_w) as executor:
                    total = len(slides)
                    futures = {
                        executor.submit(
                            generate_single_slide_image,
                            provider_key, img_api_key,
                            s["image_prompt"], s["slide_number"], total,
                            s["title"], s["body"],
                            img_quality if provider_key == "openai" else "low",
                        ): s["slide_number"]
                        for s in slides
                    }
                    done = 0
                    for future in concurrent.futures.as_completed(futures):
                        snum, img = future.result()
                        images[snum] = img
                        done += 1
                        progress.progress(done / total, text=f"[{provider_label}] {done}/{total} images done…")

                st.session_state["images"] = images
                progress.empty()
                st.success("🎉 Carousel ready! Neeche Instagram section mein post karo.")
            except Exception as e:
                st.error(f"Image generation error: {e}")

    # ── Display slides ────────────────────────────────────────────────
    if "slides_data" in st.session_state:
        data   = st.session_state["slides_data"]
        slides = data.get("slides", [])
        images = st.session_state.get("images", {})

        st.markdown(f"""
        <div style='font-family:Cormorant Garamond,serif;font-size:1.5rem;
             color:#8B0000;margin-bottom:1rem;font-weight:600;'>
            📱 Carousel Preview — {len(slides)} Slides
        </div>""", unsafe_allow_html=True)

        tabs = st.tabs([f"Slide {s['slide_number']}" for s in slides])
        for i, slide in enumerate(slides):
            with tabs[i]:
                snum = slide["slide_number"]
                if snum in images:
                    st.image(images[snum], use_container_width=True)
                    st.download_button(
                        label=f"⬇️ Download Slide {snum}",
                        data=images[snum],
                        file_name=f"wedding_slide_{snum}.png",
                        mime="image/png",
                        key=f"dl_{snum}",
                    )
                else:
                    st.markdown("""
                    <div style='background:#f5f5f5;border-radius:12px;height:180px;
                         display:flex;align-items:center;justify-content:center;color:#bbb;font-family:Lato;'>
                        🖼️ Step 2 ke baad image aayegi
                    </div>""", unsafe_allow_html=True)

                hook_html = f"<div style='font-family:Lato,sans-serif;font-size:0.82rem;font-weight:700;color:#C2185B;background:rgba(194,24,91,0.08);border-radius:8px;padding:6px 12px;margin-bottom:8px;letter-spacing:0.5px;'>🎯 HOOK: {slide.get('hook','')}</div>" if slide.get('hook') else ""
                cta_html  = f"<div style='font-family:Lato,sans-serif;font-size:0.85rem;font-weight:700;color:#fff;background:linear-gradient(135deg,#8B0000,#C2185B);border-radius:8px;padding:8px 14px;margin-top:10px;text-align:center;'>📣 {slide.get('cta','')}</div>" if slide.get('cta') else ""
                st.markdown(f"""
                <div class="slide-preview">
                    <div class="slide-num">Slide {snum}</div>
                    {hook_html}
                    <div class="slide-title">{slide.get('title','')}</div>
                    <div class="slide-body">{slide.get('body','')}</div>
                    {cta_html}
                </div>""", unsafe_allow_html=True)

        # Caption & Hashtags — always visible below carousel
        caption_val  = data.get("caption", "")
        hashtag_val  = " ".join(f"#{h}" for h in data.get("hashtags", []))
        caption_full = caption_val + "\n\n" + hashtag_val

        st.markdown("""
        <div style='font-family:Cormorant Garamond,serif;font-size:1.2rem;font-weight:600;
             color:#8B0000;margin:1.2rem 0 0.4rem;'>📝 Caption & Hashtags</div>
        """, unsafe_allow_html=True)
        st.text_area("caption_display", value=caption_full, height=130,
                     label_visibility="collapsed", key="cap_out")

        # ── Instagram Post / Schedule — always visible ────────────────
        st.markdown('<div class="insta-box">', unsafe_allow_html=True)
        st.markdown('<div class="insta-title">📸 Instagram Pe Post / Schedule Karo</div>', unsafe_allow_html=True)

        if not images:
            st.info("Pehle **Step 2 · Generate Carousel Images** click karo, phir post kar sakte ho.")
        else:
            ig_token   = ig_token_left
            ig_user_id = ig_uid_left
            imgbb_key  = imgbb_key_left

            post_type = st.radio("Kab post karna hai?", ["🚀 Abhi Post Karo", "🕐 Schedule Karo"],
                                 horizontal=True, key="post_type")

            scheduled_ts = None
            if post_type == "🕐 Schedule Karo":
                c1, c2 = st.columns(2)
                with c1:
                    sched_date = st.date_input("Date", min_value=datetime.date.today(), key="sched_d")
                with c2:
                    sched_time = st.time_input("Time", value=datetime.time(9, 0), key="sched_t")
                sched_dt = datetime.datetime.combine(sched_date, sched_time)
                scheduled_ts = int(sched_dt.timestamp())
                st.caption(f"📅 {sched_dt.strftime('%d %b %Y  ·  %I:%M %p')} ko post hoga")

            btn_post = st.button(
                "📤 Schedule on Instagram" if post_type == "🕐 Schedule Karo" else "📤 Post to Instagram Now",
                use_container_width=True, key="btn_insta",
            )
            if btn_post:
                if not ig_token or not ig_user_id or not imgbb_key:
                    st.error("Teen fields fill karo: Access Token, Account ID, imgbb Key.")
                else:
                    sorted_imgs = [images[k] for k in sorted(images.keys())]
                    try:
                        with st.spinner("📤 Images upload ho rahi hain…"):
                            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
                                urls = [f.result() for f in
                                        [ex.submit(upload_to_imgbb, imgbb_key, img) for img in sorted_imgs]]
                        with st.spinner("📸 Instagram pe post ho raha hai…"):
                            post_to_instagram(ig_token, ig_user_id, urls, caption_full, scheduled_ts)
                        if scheduled_ts:
                            st.success(f"✅ Scheduled! {sched_dt.strftime('%d %b %Y · %I:%M %p')} ko post hoga.")
                        else:
                            st.success("✅ Instagram pe carousel post ho gaya! 🎉")
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;opacity:0.4;'>
            <div style='font-size:4rem;'>🎠</div>
            <div style='font-family:Cormorant Garamond,serif;font-size:1.3rem;color:#8B0000;margin-top:1rem;'>
                Aapka carousel yahan dikhega
            </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# MONTHLY PLANNER — Full width
# ═══════════════════════════════════════════════════════════════════════

POST_TIMES = [
    ("🌅 9:00 AM",  9,  0, "9am",  "time-9am"),
    ("🌆 6:00 PM", 18,  0, "6pm",  "time-6pm"),
    ("🌙 9:00 PM", 21,  0, "9pm",  "time-9pm"),
]

st.markdown("---")
st.markdown('<div class="planner-header">📅 Monthly Carousel Planner</div>', unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;font-family:Lato,sans-serif;font-size:0.9rem;color:#888;margin-bottom:1.5rem;'>
    Topics daalo → dates assign honge → Schedule All karo → <b>laptop band karo, posts khud chalenge!</b>
</div>
""", unsafe_allow_html=True)

# ── Init session state ────────────────────────────────────────────────
if "plan_topics" not in st.session_state:
    st.session_state["plan_topics"] = []

# ── Controls row ──────────────────────────────────────────────────────
pc1, pc2, pc3 = st.columns([1, 1, 1], gap="medium")
with pc1:
    today = datetime.date.today()
    plan_month = st.selectbox("📆 Month", list(range(1, 13)),
                               index=today.month - 1,
                               format_func=lambda x: cal_lib.month_name[x],
                               key="plan_month")
with pc2:
    plan_year = st.number_input("Year", min_value=2025, max_value=2030,
                                 value=today.year, key="plan_year", label_visibility="visible")
with pc3:
    _, _last = cal_lib.monthrange(int(plan_year), plan_month)
    _default_day = min(today.day, _last)
    plan_start_day = st.number_input("Start from Day", min_value=1, max_value=_last,
                                      value=_default_day, key="plan_start_day")

# ── Topic input ───────────────────────────────────────────────────────
st.markdown('<div class="card" style="margin-top:1rem;">', unsafe_allow_html=True)
st.markdown('<div class="label">✏️ Topics Add Karo</div>', unsafe_allow_html=True)

ti1, ti2 = st.columns([5, 1])
with ti1:
    new_topic = st.text_input("topic_input", placeholder="e.g. Top 5 Wedding Decoration Trends in Nagpur 2025",
                               label_visibility="collapsed", key="new_topic_field")
with ti2:
    if st.button("➕ Add", key="btn_add_topic", use_container_width=True):
        t = new_topic.strip()
        if t and t not in st.session_state["plan_topics"]:
            st.session_state["plan_topics"].append(t)
            st.rerun()

bulk = st.text_area("Ya multiple topics paste karo (ek line = ek topic):",
                     placeholder="Bridal Lehenga Trends 2025\nMehndi Design Ideas\nWedding Mandap Decor...",
                     height=90, key="bulk_topics_field", label_visibility="visible")
cb1, cb2 = st.columns([1, 4])
with cb1:
    if st.button("Add All", key="btn_add_bulk", use_container_width=True):
        for line in bulk.strip().split("\n"):
            t = line.strip()
            if t and t not in st.session_state["plan_topics"]:
                st.session_state["plan_topics"].append(t)
        st.rerun()
with cb2:
    if st.button("🗑️ Clear All Topics", key="btn_clear_topics", use_container_width=True):
        st.session_state["plan_topics"] = []
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ── Build schedule from topics ────────────────────────────────────────
topics_list = st.session_state["plan_topics"]

_, last_day = cal_lib.monthrange(int(plan_year), plan_month)
start_date  = datetime.date(int(plan_year), plan_month, int(plan_start_day))
end_date    = datetime.date(int(plan_year), plan_month, last_day)

schedule_items = []   # [{topic, dt, time_label, key_cls, dot_cls, date}]
slot_idx  = 0
cur_date  = start_date
while cur_date <= end_date and slot_idx < len(topics_list):
    for label, hr, mn, key_cls, dot_cls in POST_TIMES:
        if slot_idx >= len(topics_list):
            break
        dt = datetime.datetime.combine(cur_date, datetime.time(hr, mn))
        schedule_items.append({
            "topic":     topics_list[slot_idx],
            "dt":        dt,
            "date":      cur_date,
            "label":     label,
            "key_cls":   key_cls,
            "dot_cls":   dot_cls,
            "idx":       slot_idx,
        })
        slot_idx += 1
    cur_date += datetime.timedelta(days=1)

days_covered = len(set(s["date"] for s in schedule_items))
days_needed  = -(-len(topics_list) // 3)   # ceil div

# ── Summary strip ─────────────────────────────────────────────────────
if topics_list:
    st.markdown(f"""
    <div style='background:rgba(194,24,91,0.06);border-radius:12px;padding:0.9rem 1.2rem;
         display:flex;gap:2rem;font-family:Lato,sans-serif;font-size:0.88rem;color:#555;
         margin-bottom:1rem;flex-wrap:wrap;'>
        <span>📌 <b style='color:#8B0000;'>{len(topics_list)}</b> topics</span>
        <span>📅 <b style='color:#8B0000;'>{days_covered}</b> days covered</span>
        <span>🕘 <b style='color:#8B0000;'>{len(schedule_items)}</b> posts scheduled</span>
        <span>📆 <b style='color:#8B0000;'>{start_date.strftime("%d %b")} → {schedule_items[-1]["date"].strftime("%d %b %Y") if schedule_items else "-"}</b></span>
    </div>
    """, unsafe_allow_html=True)

# ── Two col: Schedule list + Calendar ────────────────────────────────
pl1, pl2 = st.columns([1.2, 1], gap="large")

with pl1:
    if not topics_list:
        st.markdown("""
        <div style='text-align:center;padding:2rem;opacity:0.4;font-family:Lato,sans-serif;color:#888;'>
            Topics add karo — schedule yahan dikhega
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="label">🗓️ Schedule Preview ({len(schedule_items)} posts)</div>',
                    unsafe_allow_html=True)

        # Delete individual topics
        to_delete = None
        for i, item in enumerate(schedule_items):
            cols = st.columns([0.08, 0.18, 0.14, 0.52, 0.08])
            cols[0].markdown(f"<div style='font-family:Lato;font-size:0.75rem;color:#bbb;padding-top:6px;'>{item['idx']+1}</div>", unsafe_allow_html=True)
            cols[1].markdown(f"<div style='font-family:Lato;font-size:0.78rem;font-weight:700;color:#8B0000;padding-top:6px;'>{item['date'].strftime('%a %d %b')}</div>", unsafe_allow_html=True)
            cols[2].markdown(f"<span class='{item['key_cls']}'>{item['label'].split()[-2] + ' ' + item['label'].split()[-1]}</span>", unsafe_allow_html=True)
            cols[3].markdown(f"<div style='font-family:Lato;font-size:0.82rem;color:#444;padding-top:4px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;'>{item['topic']}</div>", unsafe_allow_html=True)
            if cols[4].button("✕", key=f"del_{item['idx']}", help="Delete"):
                to_delete = item['idx']

        if to_delete is not None:
            st.session_state["plan_topics"].pop(to_delete)
            st.rerun()

with pl2:
    # ── Mini Calendar ─────────────────────────────────────────────────
    # Build date → slots dict
    date_slots: dict = {}
    for item in schedule_items:
        d = item["date"]
        if d not in date_slots:
            date_slots[d] = []
        date_slots[d].append(item["dot_cls"])

    weeks   = cal_lib.monthcalendar(int(plan_year), plan_month)
    m_name  = f"{cal_lib.month_name[plan_month]} {plan_year}"
    dow     = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    dow_html = "".join(f"<div class='cal-dow'>{d}</div>" for d in dow)
    cells_html = ""
    for week in weeks:
        for day in week:
            if day == 0:
                cells_html += "<div class='cal-cell empty'></div>"
            else:
                d = datetime.date(int(plan_year), plan_month, day)
                slots = date_slots.get(d, [])
                has_cls = "has-posts" if slots else ""
                today_style = "border:2px solid #C2185B;" if d == today else ""
                dots = "".join(f"<span class='{dc}'></span>" for dc in slots)
                cells_html += (
                    f"<div class='cal-cell {has_cls}' style='{today_style}'>"
                    f"<span class='cal-day'>{day}</span>"
                    f"<div class='cal-dots'>{dots}</div>"
                    f"</div>"
                )

    st.markdown(f"""
    <div class="cal-wrap">
        <div class="cal-month-name">{m_name}</div>
        <div class="cal-grid">{dow_html}{cells_html}</div>
        <div class="cal-legend">
            <span><span class="dot-9am"></span> 9:00 AM</span>
            <span><span class="dot-6pm"></span> 6:00 PM</span>
            <span><span class="dot-9pm"></span> 9:00 PM</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Schedule All Button ───────────────────────────────────────────────
if schedule_items:
    st.markdown('<div class="insta-box" style="margin-top:1.5rem;">', unsafe_allow_html=True)
    st.markdown('<div class="insta-title">🚀 Generate & Schedule All to Instagram</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="help-tip">
        Yeh button click karne pe:<br>
        1️⃣ Har topic ke liye carousel content + images generate honge<br>
        2️⃣ Sab Instagram API pe schedule ho jaayenge<br>
        3️⃣ <b>Laptop band karo — Meta ke servers sahi waqt pe post karenge</b>
    </div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        plan_ig_token = st.text_input("Instagram Access Token", type="password",
                                       placeholder="EAABs...", value=_s("IG_TOKEN"), key="plan_ig_token")
    with sc2:
        plan_ig_uid = st.text_input("Instagram Account ID", placeholder="17841400...", value=_s("IG_USER_ID"), key="plan_ig_uid")
    with sc3:
        plan_imgbb = st.text_input("imgbb API Key", type="password", placeholder="abc123...", value=_s("IMGBB_KEY"), key="plan_imgbb")

    plan_claude = st.text_input("Claude API Key", type="password", placeholder="sk-ant-...", value=_s("CLAUDE_KEY"), key="plan_claude")

    plan_provider = st.radio("Image Provider:", ["Together AI (Free)", "OpenAI gpt-image-1 (Paid)"],
                              horizontal=True, key="plan_provider")
    plan_img_key = ""
    if "Together" in plan_provider:
        plan_img_key = st.text_input("Together AI Key", type="password", value=_s("TOGETHER_KEY"), key="plan_tog_key")
        plan_provider_k = "together"
    else:
        plan_img_key = st.text_input("OpenAI Key", type="password", value=_s("OPENAI_KEY"), key="plan_oai_key")
        plan_provider_k = "openai"

    plan_slides = st.slider("Slides per carousel", 3, 7, 5, key="plan_slides")

    btn_schedule_all = st.button("📅 Generate + Schedule All Posts", use_container_width=True,
                                  key="btn_schedule_all")

    if btn_schedule_all:
        missing = []
        if not plan_claude:    missing.append("Claude API Key")
        if not plan_img_key:   missing.append("Image Provider Key")
        if not plan_ig_token:  missing.append("Instagram Access Token")
        if not plan_ig_uid:    missing.append("Instagram Account ID")
        if not plan_imgbb:     missing.append("imgbb API Key")

        if missing:
            st.error(f"Ye fields fill karo: {', '.join(missing)}")
        else:
            total_posts = len(schedule_items)
            overall_bar = st.progress(0, text=f"0 / {total_posts} posts scheduled…")
            log_box     = st.empty()
            logs        = []
            success_count = 0
            fail_count    = 0

            for i, item in enumerate(schedule_items):
                log_box.markdown(
                    f"⏳ **[{i+1}/{total_posts}]** `{item['date'].strftime('%d %b')} {item['label']}` — {item['topic'][:50]}…"
                )
                try:
                    # Step A: Generate slide content via Claude
                    slide_data = generate_slides_content(
                        plan_claude, item["topic"], plan_slides, "Elegant & Romantic", "Instagram"
                    )
                    slides_for_item = slide_data["slides"]
                    cap  = slide_data.get("caption", "")
                    tags = " ".join(f"#{h}" for h in slide_data.get("hashtags", []))
                    caption_full = cap + "\n\n" + tags

                    # Step B: Generate images
                    imgs = {}
                    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
                        futs = {
                            ex.submit(
                                generate_single_slide_image,
                                plan_provider_k, plan_img_key,
                                s["image_prompt"], s["slide_number"], len(slides_for_item),
                                s["title"], s["body"], "low",
                            ): s["slide_number"]
                            for s in slides_for_item
                        }
                        for f in concurrent.futures.as_completed(futs):
                            sn, ib = f.result()
                            imgs[sn] = ib

                    sorted_imgs = [imgs[k] for k in sorted(imgs.keys())]

                    # Step C: Upload to imgbb
                    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
                        urls = [f.result() for f in
                                [ex.submit(upload_to_imgbb, plan_imgbb, img) for img in sorted_imgs]]

                    # Step D: Schedule on Instagram
                    sched_ts = int(item["dt"].timestamp())
                    post_to_instagram(plan_ig_token, plan_ig_uid, urls, caption_full, sched_ts)

                    success_count += 1
                    logs.append(f"✅ {item['date'].strftime('%d %b')} {item['label']} — {item['topic'][:45]}")

                except Exception as e:
                    fail_count += 1
                    logs.append(f"❌ {item['date'].strftime('%d %b')} {item['label']} — Error: {str(e)[:60]}")

                overall_bar.progress((i + 1) / total_posts,
                                     text=f"{i+1}/{total_posts} done · ✅{success_count} ❌{fail_count}")

            log_box.empty()
            if fail_count == 0:
                st.success(f"🎉 Sab {success_count} posts schedule ho gaye! Laptop band karo — Meta sahi waqt pe post karega.")
            else:
                st.warning(f"✅ {success_count} scheduled, ❌ {fail_count} failed.")

            with st.expander("📋 Detail Log"):
                for l in logs:
                    st.markdown(l)

    st.markdown('</div>', unsafe_allow_html=True)
