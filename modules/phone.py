import os
import math
import random
from PIL import Image, ImageDraw, ImageFont
import qrcode

from modules.output_utils import unique_output_path

# --- Configuration Section ---
SIZE = (800, 800)
BG_COLOR = (11, 19, 26)         # Deep Cyber Tech Blue-Black
PREDICTIVE_COLOR = (0, 229, 255) # Cyber Cyan for Forecast Target
TEXT_COLOR = (255, 255, 255)

def get_phone_growth_data(model_name):
    """
    போன்களின் உலகளாவிய சந்தை வளர்ச்சி தரவுகள் (Global Shipment Volume in Million Units).
    கடந்த 4 காலாண்டு / வருட விற்பனை (2023 - 2026) மற்றும் அடுத்த 2 வருட இலக்கு.
    """
    mname = model_name.upper()
    
    if "IPHONE" in mname or "APPLE" in mname:
        return [75, 82, 89, 95], [102, 110]
    elif "SAMSUNG" in mname or "GALAXY" in mname:
        return [80, 85, 91, 98], [105, 112]
    elif "ONEPLUS" in mname or "NOTHING" in mname:
        return [12, 18, 25, 32], [38, 45]
    else:
        return [20, 28, 35, 42], [48, 55]

def draw_hexagon(draw, center, size, color, width=1):
    points = []
    for i in range(6):
        angle = math.radians(60 * i)
        px = center[0] + size * math.cos(angle)
        py = center[1] + size * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, outline=color, width=width)

def generate_phone_logo(model_id, brand_name, font_selection="Classic Standard (Arial)", output_dir="generated/phone", show_dialog=True):
    # FETCH LOCAL DATA MATRIX
    raw_actuals, raw_predicts = get_phone_growth_data(model_id)
    
    all_vals = raw_actuals + raw_predicts
    min_v, max_v = min(all_vals), max(all_vals)
    span = (max_v - min_v) if max_v != min_v else 1
    
    # Strictly compressed bar heights to leave comfortable room for text grids safely
    ACTUAL_DATA_POINTS = [50 + ((v - min_v) / span) * 140 for v in raw_actuals]
    PREDICTIVE_DATA_POINTS = [50 + ((v - min_v) / span) * 140 for v in raw_predicts]

    growth_pct = ((raw_actuals[-1] - raw_actuals[0]) / raw_actuals[0]) * 100
    avg_sales = sum(raw_actuals) / len(raw_actuals)
    
    # Derived Smartphone Analytics Metrics
    is_premium = "IPHONE" in model_id.upper() or "APPLE" in model_id.upper()
    sigma_volatility = round(1.85 + (growth_pct * 0.012) if is_premium else 1.25 + (growth_pct * 0.006), 2)
    drift_acceleration = round(growth_pct * 0.32, 1)

    # Electric Neon Purple Accent for Premium Smartphone Vibe
    ACENT_COLOR = (168, 85, 247) 
    theme_status = "OPTIMAL DEVICE VELOCITY MATRIX"

    # Create Canvas Graphic Space
    image = Image.new("RGBA", SIZE, BG_COLOR)
    draw = ImageDraw.Draw(image)

    # Dynamic Font System Configurations Locked In
    font_files = {
        "Classic Standard (Arial)": "C:\\Windows\\Fonts\\arialbd.ttf",
        "Artistic Stylized (Gabriola)": "C:\\Windows\\Fonts\\gabriola.ttf",
        "Cursive Script (Vladimir)": "C:\\Windows\\Fonts\\vladimir.ttf",
        "Playful Stylized (Comic Bold)": "C:\\Windows\\Fonts\\comicbd.ttf"
    }
    
    CHOSEN_FONT_PATH = font_files.get(font_selection, "C:\\Windows\\Fonts\\arialbd.ttf")
    FONT_STYLE_MATH = "C:\\Windows\\Fonts\\seguisym.ttf" 
    FONT_STYLE_SERIF = "C:\\Windows\\Fonts\\cambriab.ttf"

    try:
        brand_giant_letter = ImageFont.truetype(CHOSEN_FONT_PATH, 160) 
        brand_text_font = ImageFont.truetype(CHOSEN_FONT_PATH, 50 if len(model_id) < 12 else 40)
        math_equation_font = ImageFont.truetype(FONT_STYLE_SERIF, 15) 
        math_notations_font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 20)
        small_label_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 13)
        glossary_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 11)
        giant_icon_font = ImageFont.truetype(FONT_STYLE_MATH, 65)
    except IOError:
        brand_giant_letter = brand_text_font = math_equation_font = ImageFont.load_default()
        math_notations_font = small_label_font = glossary_font = giant_icon_font = ImageFont.load_default()

    # NOTE: Background Scatter Symbols have been completely removed from here to clean up space.

    # Structural Stability Rings (Hexagon Frame)
    center_canvas = (SIZE[0] // 2, SIZE[1] // 2)
    draw_hexagon(draw, center_canvas, 340, (40, 55, 75, 80), width=3)
    
    circle_radius = 338
    circle_box = [center_canvas[0]-circle_radius, center_canvas[1]-circle_radius, center_canvas[0]+circle_radius, center_canvas[1]+circle_radius]
    draw.ellipse(circle_box, outline=(168, 85, 247, 15), width=2)

    # BRAND CENTER TYPOGRAPHY LOCKED SYSTEM
    first_letter = model_id[0].upper() if model_id else "P"
    full_name = model_id.upper()
    brand_y_anchor = 110 
    
    total_text_width = 0
    letter_spacing_gap = 10 if len(full_name) > 8 else 14
    for letter in full_name:
        left, top, right, bottom = draw.textbbox((0, 0), letter, font=brand_text_font)
        total_text_width += (right - left) + letter_spacing_gap
    total_text_width -= letter_spacing_gap
    brand_x_centered = (SIZE[0] - total_text_width) // 2

    gw_l, gw_t, gw_r, gw_b = draw.textbbox((0, 0), first_letter, font=brand_giant_letter)
    gw_x = (SIZE[0] - (gw_r - gw_l)) // 2
    draw.text((gw_x, brand_y_anchor - 25), first_letter, fill=(168, 85, 247, 12), font=brand_giant_letter)
    
    current_x = brand_x_centered
    for letter in full_name:
        text_color_pick = "white" if letter != first_letter else ACENT_COLOR
        draw.text((current_x, brand_y_anchor + 80), letter, fill=text_color_pick, font=brand_text_font)
        left, top, right, bottom = draw.textbbox((0, 0), letter, font=brand_text_font)
        current_x += (right - left) + letter_spacing_gap

    # =========================================================================
    # 📐 SYMMETRICAL RE-ALIGNED QUADRANTS SYSTEM (Perfect Grid Alignment)
    # =========================================================================
    left_margin = 110
    right_margin = 485
    top_text_y = 95  
    
    # QUADRANT 1: TOP-LEFT (Cleaned up from overlapping background noise)
    draw.text((left_margin, top_text_y), "[DEVICE PROFILE MATRIX]", fill=(100, 116, 139), font=small_label_font)
    draw.text((left_margin, top_text_y + 23), f"MODEL INDEX: {model_id} // {brand_name}", fill=(148, 163, 184), font=small_label_font)
    draw.text((left_margin, top_text_y + 53), "Hardware Integrity Grid ➔ Active", fill=(71, 85, 105), font=math_equation_font)
    
    # QUADRANT 2: TOP-RIGHT 
    draw.text((right_margin, top_text_y), "[TECH ADOPTION RATIO]", fill=(100, 116, 139), font=small_label_font)
    draw.text((right_margin, top_text_y + 23), f"Shipment Trend ➔ +{round(growth_pct, 1)}%", fill=(148, 163, 184), font=small_label_font)
    draw.text((right_margin, top_text_y + 53), "User Ecosystem Longevity Map", fill=(71, 85, 105), font=math_equation_font)
    
    # QUADRANT 3: CENTER-LEFT
    draw.text((left_margin, 370), "[MARKET DEMAND MODEL]", fill=(100, 116, 139), font=small_label_font)
    draw.text((left_margin, 395), f"μ (Mean Volume): {round(avg_sales, 1)}M Units", fill=ACENT_COLOR, font=math_notations_font)
    draw.text((left_margin, 423), f"Performance: {theme_status.split()[0]}", fill=(120, 140, 160), font=small_label_font)
    
    # QUADRANT 4: FIXED BOTTOM-LEFT BOUNDARY
    draw.text((left_margin, 505), "[CONSUMER AUDIT DATA]", fill=(100, 116, 139), font=small_label_font)
    draw.text((left_margin, 530), "Status ➔ PREDICTIVE LIFECYCLE VECTOR", fill=TEXT_COLOR, font=small_label_font)

    # --- 📊 CENTRAL RIGHT GRID: COMPRESSED BALANCED BAR CHART ---
    bar_w, gap = 32, 20
    start_x = 425  
    base_y = 440 
    last_x, last_y = 0, 0
    years_labels = ["2023", "2024", "2025", "2026"]

    for i, h in enumerate(ACTUAL_DATA_POINTS):
        x1 = start_x + (i * (bar_w + gap))
        y1 = base_y - h
        x2 = x1 + bar_w
        
        draw.rectangle([x1, y1 + 10, x2, base_y], fill=(30, 45, 60))
        draw.ellipse([x1, y1, x2, y1 + 16], fill=ACENT_COLOR)
        
        sales_display = f"{raw_actuals[i]}M"
        draw.text((x1 - 2, y1 - 22), sales_display, fill=ACENT_COLOR, font=small_label_font)
        draw.text((x1 + 2, base_y + 8), years_labels[i], fill=(140, 150, 165), font=small_label_font)
        
        if i == len(ACTUAL_DATA_POINTS)-1: 
            last_x, last_y = x1 + (bar_w // 2), y1 + 8

    # Predictive Future Projections Vector
    for j, h in enumerate(PREDICTIVE_DATA_POINTS):
        cx = start_x + ((len(ACTUAL_DATA_POINTS) + j) * (bar_w + gap)) + (bar_w // 2)
        cy = base_y - h
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=PREDICTIVE_COLOR)
        draw.line([(last_x, last_y), (cx, cy)], fill=PREDICTIVE_COLOR, width=2)
        
        if j == 0: 
            draw.text((cx - 15, cy - 22), "Target ➔", fill=PREDICTIVE_COLOR, font=small_label_font)
        last_x, last_y = cx, cy

    # QUADRANT 5: OUTPUT METRICS DIRECTLY BELOW BAR GRAPH POSITION
    draw.text((right_margin, 475), "[OUTPUT METRICS SYSTEMS]", fill=(100, 116, 139), font=small_label_font)
    draw.text((right_margin, 500), f"σ (Volatility Index) ➔ {sigma_volatility}x", fill=PREDICTIVE_COLOR, font=math_notations_font)
    draw.text((right_margin, 530), "Ecosystem Future Target Met", fill=(71, 85, 105), font=math_equation_font)

    # =========================================================================
    # 📖 📱 SMARTPHONE METRICS GLOSSARY BOX CONTAINER 
    # =========================================================================
    box_x1, box_y1, box_x2, box_y2 = 105, 575, 515, 742
    draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline=(40, 55, 75), fill=(12, 18, 24), width=2)
    
    glossary_y = box_y1 + 8
    line_spacing = 14
    draw.text((box_x1 + 15, glossary_y), "─── SMARTPHONE METRICS GLOSSARY ───", fill=ACENT_COLOR, font=small_label_font)
    draw.text((box_x1 + 15, glossary_y + 18), f"μ (Mean Volume)  : Cumulative Average Shipment Strength of Devices ({round(avg_sales, 1)}M)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + line_spacing), f"σ (Volatility)   : Supply Chain Volatility Yield Deviation Factor ({sigma_volatility}x)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 2)), f"ΔM/Δt (Drift)    : Brand Adoption Growth Enhancement Velocity Rate (+{drift_acceleration}%)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 3)), "∑ (Summation)    : Global Shipment Volume Units Across All Quarters", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 4)), "Ecosystem Vector : OS Security Feature & Software Update Lifespan", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 5)), "Target Vector    : Predictive Institutional Future Milestone Goals", fill=(148, 163, 184), font=glossary_font)

    # Footer Setup
    draw.text((105, 755), f"SMARTPHONE VALUE ANALYTICS CONTROLLER v2.8 - ID: {model_id}", fill=(100, 116, 139), font=small_label_font)

    # =========================================================================
    # 🛠️ QR POSITION & SCALE (Perfect right alignment inside grid limits)
    # =========================================================================
    qr_url = "https://www.gsmarena.com/"
    qr_gen = qrcode.QRCode(version=1, box_size=4, border=1)
    qr_gen.add_data(qr_url)
    qr_gen.make(fit=True)
    
    qr_img = qr_gen.make_image(fill_color="white", back_color=BG_COLOR).convert("RGBA")
    qw, qh = qr_img.size
    
    qr_target_x = SIZE[0] - qw - 105
    qr_target_y = box_y1 + ((box_y2 - box_y1) - qh) // 2  
    
    image.paste(qr_img, (qr_target_x, qr_target_y), qr_img)
    # =========================================================================

    output_path = unique_output_path(output_dir, model_id)
    image.save(output_path, "PNG")
    if show_dialog:
        from tkinter import messagebox

        messagebox.showinfo("Success", f"Symmetrical Smartphone Growth Vector Rendered!")
    return output_path


def generate_phone(model_id, brand_name, style, output_dir="generated/phone"):
    return generate_phone_logo(model_id, brand_name, style, output_dir, show_dialog=False)

# --- Tkinter Application Engine Interface ---
def run_app():
    import tkinter as tk
    from tkinter import messagebox
    from PIL import ImageTk

    def on_generate():
        m_id = e1.get().strip()
        b_name = e2.get().strip()
        selected_style = font_var.get() 
        if m_id and b_name:
            filename = generate_phone_logo(m_id.upper(), b_name.upper(), selected_style)
            img_res = Image.open(filename)
            tk_img = ImageTk.PhotoImage(img_res.resize((480, 480)))
            canvas_label.config(image=tk_img)
            canvas_label.image = tk_img
        else:
            messagebox.showwarning("Input Error", "Please fill Smartphone Credentials properly.")

    root = tk.Tk()
    root.title("Smartphone Ecosystem Analytics Dashboard")
    root.geometry("560x860")
    root.configure(bg="#0B131A")

    tk.Label(root, text="Mobile Model Designation (e.g., IPHONE15, GALAXYS24):", bg="#0B131A", fg="white", font=("Arial", 10)).pack(pady=5)
    e1 = tk.Entry(root, font=("Arial", 11), justify="center", width=25); e1.insert(0, "IPHONE15"); e1.pack()
    
    tk.Label(root, text="Parent Tech Corporation Brand (e.g., APPLE, SAMSUNG):", bg="#0B131A", fg="white", font=("Arial", 10)).pack(pady=5)
    e2 = tk.Entry(root, font=("Arial", 11), justify="center", width=25); e2.insert(0, "APPLE"); e2.pack()

    tk.Label(root, text="Select Custom Typography Text Style:", bg="#0B131A", fg="#A855F7", font=("Arial", 10, "bold")).pack(pady=8)
    
    font_options = ["Classic Standard (Arial)", "Artistic Stylized (Gabriola)", "Cursive Script (Vladimir)", "Playful Stylized (Comic Bold)"]
    font_var = tk.StringVar(root)
    font_var.set(font_options[0]) 
    
    font_dropdown = tk.OptionMenu(root, font_var, *font_options)
    font_dropdown.config(font=("Arial", 10), bg="#1E293B", fg="white", activebackground="#334155")
    font_dropdown.pack(pady=5)

    btn = tk.Button(root, text="ANALYZE ECOSYSTEM GROWTH & RENDER", command=on_generate, bg="#A855F7", fg="white", font=("Arial", 11, "bold"), padx=10, pady=7)
    btn.pack(pady=20)

    canvas_label = tk.Label(root, bg="#0B131A")
    canvas_label.pack()

    root.mainloop()

if __name__ == "__main__":
    run_app()