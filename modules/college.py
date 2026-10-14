import os
import math
import random
from PIL import Image, ImageDraw, ImageFont
import qrcode

from modules.output_utils import unique_output_path

# --- Configuration Section ---
SIZE = (800, 800)
BG_COLOR = (12, 12, 18)        # Premium Dark Velvet Blue
PREDICTIVE_COLOR = (0, 229, 255) # Cyber Cyan for Forecast
TEXT_COLOR = (255, 255, 255)

def get_psgcas_placement_data(institution_id):
    if "PSG" in institution_id.upper():
        actuals = [1150, 1420, 1680, 1950] 
        predictive = [2150, 2400]
        return actuals, predictive
    else:
        return [500, 650, 800, 950], [1100, 1250]

def draw_hexagon(draw, center, size, color, width=1):
    points = []
    for i in range(6):
        angle = math.radians(60 * i)
        px = center[0] + size * math.cos(angle)
        py = center[1] + size * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, outline=color, width=width)

def generate_college_logo(college_id, college_name, font_selection="Classic Standard (Arial)", output_dir="generated/college", show_dialog=True):
    raw_actuals, raw_predicts = get_psgcas_placement_data(college_id)
    
    # Normalization Scaling (Strictly mapped to match original corporate bar height range)
    all_vals = raw_actuals + raw_predicts
    min_v, max_v = min(all_vals), max(all_vals)
    span = (max_v - min_v) if max_v != min_v else 1
    
    ACTUAL_DATA_POINTS = [80 + ((v - min_v) / span) * 220 for v in raw_actuals]
    PREDICTIVE_DATA_POINTS = [80 + ((v - min_v) / span) * 220 for v in raw_predicts]

    growth_pct = ((raw_actuals[-1] - raw_actuals[0]) / raw_actuals[0]) * 100
    avg_placed = int(sum(raw_actuals)/len(raw_actuals))
    
    # Advanced Derived Placement Metrics
    alpha_trust = round(growth_pct * 0.12, 2)
    rho_stability = round(1.1 + (growth_pct * 0.01), 2)
    lambda_drive_share = round(max(5.0, min(95.0, 55.0 + (growth_pct * 0.8))), 1)

    ACENT_COLOR = (255, 215, 0) # Royal Gold
    image = Image.new("RGBA", SIZE, BG_COLOR)
    draw = ImageDraw.Draw(image)

    # --- Safe Font Loader ---
    font_files = {
        "Artistic Stylized (Gabriola)": "C:\\Windows\\Fonts\\gabriola.ttf",
        "Cursive Script (Vladimir)": "C:\\Windows\\Fonts\\vladimir.ttf",
        "Playful Stylized (Comic Bold)": "C:\\Windows\\Fonts\\comicbd.ttf",
        "Classic Standard (Arial)": "C:\\Windows\\Fonts\\arialbd.ttf"
    }
    CHOSEN_FONT_PATH = font_files.get(font_selection, "C:\\Windows\\Fonts\\arialbd.ttf")

    try:
        brand_giant_letter = ImageFont.truetype(CHOSEN_FONT_PATH, 180)
        brand_text_font = ImageFont.truetype(CHOSEN_FONT_PATH, 65)
        math_equation_font = ImageFont.truetype("C:\\Windows\\Fonts\\cambriab.ttf", 18) 
        math_notations_font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 22)
        small_label_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 14)
        glossary_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 11) 
    except IOError:
        brand_giant_letter = brand_text_font = math_equation_font = ImageFont.load_default()
        math_notations_font = small_label_font = glossary_font = ImageFont.load_default()

    # Perfect Radiated Background Circle & Hexagon Systems
    center_canvas = (SIZE[0] // 2, SIZE[1] // 2)
    draw_hexagon(draw, center_canvas, 340, (50, 50, 70, 100), width=3)
    
    # Flawless Geometric Radial Circle Core Bounds
    circle_radius = 338
    circle_box = [center_canvas[0]-circle_radius, center_canvas[1]-circle_radius, center_canvas[0]+circle_radius, center_canvas[1]+circle_radius]
    draw.ellipse(circle_box, outline=(255, 215, 0, 15), width=2)

    # 🏢 INSTITUTION CENTER LOGO CORE
    first_letter = college_name[0].upper() if college_name else "P"
    full_name = college_name.upper()
    brand_y_anchor = 110 
    
    total_text_width = 0
    letter_spacing_gap = 14
    for letter in full_name:
        left, top, right, bottom = draw.textbbox((0, 0), letter, font=brand_text_font)
        total_text_width += (right - left) + letter_spacing_gap
    total_text_width -= letter_spacing_gap
    brand_x_centered = (SIZE[0] - total_text_width) // 2
    
    gw_l, gw_t, gw_r, gw_b = draw.textbbox((0, 0), first_letter, font=brand_giant_letter)
    gw_x = (SIZE[0] - (gw_r - gw_l)) // 2
    draw.text((gw_x, brand_y_anchor - 25), first_letter, fill=(255, 215, 0, 12), font=brand_giant_letter)

    current_x = brand_x_centered
    for letter in full_name:
        text_color_pick = "white" if letter != first_letter else ACENT_COLOR
        draw.text((current_x, brand_y_anchor + 80), letter, fill=text_color_pick, font=brand_text_font)
        left, top, right, bottom = draw.textbbox((0, 0), letter, font=brand_text_font)
        current_x += (right - left) + letter_spacing_gap

    # =========================================================================
    # 📐 PLACEMENT COORDINATES GRID LAYER (Untouched Position Matrix)
    # =========================================================================
    
    # TOP LEFT & RIGHT BLOCKS
    draw.text((70, 65), "[CAMPUS SUCCESS MATRIX]", fill=(100, 116, 139), font=small_label_font)
    draw.text((70, 88), f"α (Corporate Trust) ➔ +{alpha_trust}%", fill=ACENT_COLOR, font=math_notations_font)
    draw.text((70, 118), "η Institutional Tier-1 NIRF Active", fill=(71, 85, 105), font=math_equation_font)
    
    draw.text((515, 65), "[TOTAL PLACEMENT POOL]", fill=(100, 116, 139), font=small_label_font)
    draw.text((515, 88), f"∑ Alumnus Base = {int(sum(raw_actuals))}+", fill=ACENT_COLOR, font=math_notations_font)
    draw.text((515, 118), "∂ Academic Demand Drift Matrix", fill=(71, 85, 105), font=math_equation_font)
    
    # MIDDLE LEFT BLOCKS
    draw.text((70, 370), "[BATCH DEMAND ENGINE]", fill=(100, 116, 139), font=small_label_font)
    draw.text((70, 395), f"ρ (Consistency) ➔ {rho_stability}x Yield", fill=TEXT_COLOR, font=small_label_font)
    draw.text((70, 420), f"g (Avg Hired/Yr) ➔ {avg_placed}+", fill=ACENT_COLOR, font=math_notations_font)
    
    # BOTTOM LEFT BLOCKS
    draw.text((70, 505), "[PLACEMENT AUDIT PROFILE]", fill=(100, 116, 139), font=small_label_font)
    draw.text((70, 530), f"β (Market Risk Shield) = 0.95", fill=TEXT_COLOR, font=small_label_font)

    # --- 📊 ORIGINAL POSITIONING BAR CHART CORE (FIRST UNTOUCHED POSITION) ---
    bar_w, gap = 38, 24
    start_x = 440  
    base_y = 440   # Restored original base height coordinate profile
    last_x, last_y = 0, 0
    years_labels = ["2022", "2023", "2024", "2025"]

    for i, h in enumerate(ACTUAL_DATA_POINTS):
        x1 = start_x + (i * (bar_w + gap))
        y1 = base_y - h
        x2 = x1 + bar_w
        
        draw.rectangle([x1, y1 + 10, x2, base_y], fill=(40, 40, 60))
        draw.ellipse([x1, y1, x2, y1 + 16], fill=ACENT_COLOR)
        
        display_count = f"{raw_actuals[i]}"
        draw.text((x1, y1 - 22), display_count, fill=ACENT_COLOR, font=small_label_font)
        draw.text((x1 + 2, base_y + 8), years_labels[i], fill=(150, 160, 180), font=small_label_font)
        if i == len(ACTUAL_DATA_POINTS)-1: 
            last_x, last_y = x1 + (bar_w // 2), y1 + 8

    for j, h in enumerate(PREDICTIVE_DATA_POINTS):
        cx = start_x + ((len(ACTUAL_DATA_POINTS) + j) * (bar_w + gap)) + (bar_w // 2)
        cy = base_y - h
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=PREDICTIVE_COLOR)
        draw.line([(last_x, last_y), (cx, cy)], fill=PREDICTIVE_COLOR, width=2)
        last_x, last_y = cx, cy

    # =========================================================================
    # 🎯 LAMBDA PLACED DIRECTLY BELOW THE ORIGINAL BAR GRAPH POSITION
    # =========================================================================
    draw.text((515, 475), "[CAMPUS DRIVE DOMINANCE]", fill=(100, 116, 139), font=small_label_font)
    draw.text((515, 500), f"λ (Lambda) ➔ {lambda_drive_share}% Share", fill=PREDICTIVE_COLOR, font=math_notations_font)
    draw.text((515, 530), "Sector Selection Share Core", fill=(71, 85, 105), font=math_equation_font)

    # =========================================================================
    # 📖 🎓 PLACEMENT SYMBOL GLOSSARY CONTAINER BOX (Y: 575 to 740)
    # =========================================================================
    box_x1, box_y1, box_x2, box_y2 = 70, 575, 535, 742
    draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline=(50, 50, 70), fill=(15, 15, 24), width=2)
    
    glossary_y = box_y1 + 8
    line_spacing = 14
    draw.text((box_x1 + 15, glossary_y), "CAMPUS PLACEMENT SYMBOLS GLOSSARY", fill=ACENT_COLOR, font=small_label_font)
    draw.text((box_x1 + 15, glossary_y + 18), f"g (Mean Hired)   : Varuda Saramsari Vaelaivaaippu Mathippu ({avg_placed}+ Students)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + line_spacing), f"β (Market Shield): Velivatta Economic Crisis Sariyum Podhum Placement Pathugaapu", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 2)), f"α (Trust Index)  : Corporate Nambikkai Alavu (Institutional Value Return = {alpha_trust}%)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 3)), f"ρ (Consistency)  : Thodarchaana Placement Unmaiyana Seerthanam Factor", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 4)), f"λ (Drive Share)  : Santhai Drive Aathikkam (Market Recruitment Share = {lambda_drive_share}%)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 5)), f"∑ (Summation)    : Motha Kootu Alumnus Strength Record Data Matrix ({int(sum(raw_actuals))}+ Offers)", fill=(148, 163, 184), font=glossary_font)

    # Footers
    draw.text((70, 755), f"CAMPUS METRIC IDENTITY CONTROLLER v3.2 - ID: {college_id}", fill=(100, 116, 139), font=small_label_font)

    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(f"https://www.psgcas.ac.in/")
    qr_img = qr.make_image(fill_color="white", back_color=BG_COLOR).convert("RGBA")
    image.paste(qr_img, (SIZE[0]-qr_img.size[0]-70, SIZE[1]-qr_img.size[1]-60))

    output_path = unique_output_path(output_dir, college_id)
    image.save(output_path, "PNG")
    if show_dialog:
        from tkinter import messagebox

        messagebox.showinfo("Success", f"Symmetrical Academic Framework Loaded for {college_name}!")
    return output_path


def generate_college(college_id, college_name, style, output_dir="generated/college"):
    return generate_college_logo(college_id, college_name, style, output_dir, show_dialog=False)

# --- UI Framework (Tkinter) ---
def run_app():
    import tkinter as tk
    from tkinter import messagebox
    from PIL import ImageTk

    def on_generate():
        cid = e1.get().strip()
        cname = e2.get().strip()
        selected_font = font_var.get()
        if cid and cname:
            filename = generate_college_logo(cid.upper(), cname.upper(), selected_font)
            img_res = Image.open(filename)
            tk_img = ImageTk.PhotoImage(img_res.resize((480, 480)))
            canvas_label.config(image=tk_img)
            canvas_label.image = tk_img
        else:
            messagebox.showwarning("Input Error", "Please fill College ID and Name properly.")

    root = tk.Tk()
    root.title("Academic Placement Branding Dashboard System")
    root.geometry("560x840")
    root.configure(bg="#111517")

    tk.Label(root, text="College ID / Ticker (e.g. PSGCAS):", bg="#111517", fg="white", font=("Arial", 10)).pack(pady=5)
    e1 = tk.Entry(root, font=("Arial", 11), justify="center"); e1.insert(0, "PSGCAS"); e1.pack()
    
    tk.Label(root, text="Display College Name (e.g. PSGCAS):", bg="#111517", fg="white", font=("Arial", 10)).pack(pady=5)
    e2 = tk.Entry(root, font=("Arial", 11), justify="center"); e2.insert(0, "PSGCAS"); e2.pack()

    tk.Label(root, text="Select Custom Typography Text Style:", bg="#111517", fg="#FFD700", font=("Arial", 10, "bold")).pack(pady=8)
    
    font_options = ["Classic Standard (Arial)", "Artistic Stylized (Gabriola)", "Cursive Script (Vladimir)", "Playful Stylized (Comic Bold)"]
    font_var = tk.StringVar(root)
    font_var.set(font_options[0]) 
    
    font_dropdown = tk.OptionMenu(root, font_var, *font_options)
    font_dropdown.config(font=("Arial", 10), bg="#1E293B", fg="white", activebackground="#334155")
    font_dropdown.pack(pady=5)

    btn = tk.Button(root, text="GENERATE PLACEMENT LOGO", command=on_generate, bg="#FFD700", fg="black", font=("Arial", 11, "bold"), padx=10, pady=5)
    btn.pack(pady=15)

    canvas_label = tk.Label(root, bg="#111517")
    canvas_label.pack()

    root.mainloop()

if __name__ == "__main__":
    run_app()
