import os
import math
import random
from PIL import Image, ImageDraw, ImageFont
import qrcode

from modules.output_utils import unique_output_path

# --- Configuration Section ---
SIZE = (800, 800)
BG_COLOR = (10, 16, 26)         # Deep High-Tech Blue-Black
PREDICTIVE_COLOR = (0, 229, 255) # Cyber Cyan for Forecast Target
TEXT_COLOR = (255, 255, 255)

def get_school_performance_data(school_id, school_name, board_type):
    """
    School details matrix data module - Maps scores based on identity.
    """
    sid = school_id.upper()
    sname = school_name.upper()
    
    is_govt = "GHS" in sid or "GHSS" in sid or "GOVT" in sname
    
    if board_type == "12th Board (HSC)":
        if is_govt:
            return [86, 89, 92, 95], [98, 100]  
        else:
            return [94, 96, 98, 99], [100, 100] 
    else: 
        if is_govt:
            return [88, 91, 94, 96], [99, 100]  
        else:
            return [96, 97, 99, 99], [100, 100] 

def draw_hexagon(draw, center, size, color, width=1):
    points = []
    for i in range(6):
        angle = math.radians(60 * i)
        px = center[0] + size * math.cos(angle)
        py = center[1] + size * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, outline=color, width=width)

def generate_school_logo(school_id, school_name, board_type, font_selection="Classic Standard (Arial)", output_dir="generated/school", show_dialog=True):
    raw_actuals, raw_predicts = get_school_performance_data(school_id, school_name, board_type)
    
    # Normalization Scaling
    all_vals = raw_actuals + raw_predicts
    min_v, max_v = min(all_vals), max(all_vals)
    span = (max_v - min_v) if max_v != min_v else 1
    
    ACTUAL_DATA_POINTS = [80 + ((v - min_v) / span) * 140 for v in raw_actuals]
    PREDICTIVE_DATA_POINTS = [80 + ((v - min_v) / span) * 140 for v in raw_predicts]

    growth_improvement = raw_actuals[-1] - raw_actuals[0]
    avg_pass = sum(raw_actuals) / len(raw_actuals)
    
    # Advanced Derived School Metrics
    alpha_trust = round(growth_improvement * 1.2, 2)
    rho_stability = round(1.05 + (growth_improvement * 0.02), 2)
    
    # Dynamic Centum Count Logic based on performance
    is_govt = "GHS" in school_id.upper() or "GHSS" in school_id.upper()
    past_year_centums = int(max(2, round(growth_improvement * (1.5 if not is_govt else 0.8))))

    ACENT_COLOR = (255, 40, 132) # Vibrant Pink Accent Color
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
        title_font_size = 50 if len(school_name) < 12 else 40
        brand_giant_letter = ImageFont.truetype(CHOSEN_FONT_PATH, 160)
        brand_text_font = ImageFont.truetype(CHOSEN_FONT_PATH, title_font_size)
        math_equation_font = ImageFont.truetype("C:\\Windows\\Fonts\\cambriab.ttf", 15) 
        math_notations_font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 20)
        small_label_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 13)
        glossary_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 11) 
    except IOError:
        brand_giant_letter = brand_text_font = math_equation_font = math_notations_font = small_label_font = glossary_font = ImageFont.load_default()

    # Perfect Radiated Background Circle & Hexagon Systems
    center_canvas = (SIZE[0] // 2, SIZE[1] // 2)
    draw_hexagon(draw, center_canvas, 340, (40, 52, 72, 80), width=3)
    
    circle_radius = 338
    circle_box = [center_canvas[0]-circle_radius, center_canvas[1]-circle_radius, center_canvas[0]+circle_radius, center_canvas[1]+circle_radius]
    draw.ellipse(circle_box, outline=(255, 40, 132, 15), width=2)

    # 🏫 INSTITUTION CENTER LOGO CORE
    first_letter = school_name[0].upper() if school_name else "S"
    full_name = school_name.upper()
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
    draw.text((gw_x, brand_y_anchor - 25), first_letter, fill=(255, 40, 132, 12), font=brand_giant_letter)

    current_x = brand_x_centered
    for letter in full_name:
        text_color_pick = "white" if letter != first_letter else ACENT_COLOR
        draw.text((current_x, brand_y_anchor + 80), letter, fill=text_color_pick, font=brand_text_font)
        left, top, right, bottom = draw.textbbox((0, 0), letter, font=brand_text_font)
        current_x += (right - left) + letter_spacing_gap

    # =========================================================================
    # 📐 FIXED: MATHEMATICAL TEXT LAYERS (Shifted down to avoid overlapping background lines)
    # =========================================================================
    left_margin = 110
    right_margin = 485
    top_text_y = 95  # Increased from 75 to safely clear the hexagon's top lines
    
    # TOP LEFT & RIGHT BLOCKS
    draw.text((left_margin, top_text_y), "[ACADEMIC SUCCESS MATRIX]", fill=(100, 116, 139), font=small_label_font)
    draw.text((left_margin, top_text_y + 23), f"α (Academic Growth) ➔ +{alpha_trust}%", fill=ACENT_COLOR, font=math_notations_font)
    draw.text((left_margin, top_text_y + 53), f"EMIS Evaluation Grid: {board_type.split()[0]} Active", fill=(71, 85, 105), font=math_equation_font)
    
    draw.text((right_margin, top_text_y), "[ACADEMIC BATCH POOL]", fill=(100, 116, 139), font=small_label_font)
    draw.text((right_margin, top_text_y + 23), f"∑ Pass Rate Mean = {round(avg_pass, 1)}%", fill=ACENT_COLOR, font=math_notations_font)
    draw.text((right_margin, top_text_y + 53), "∂ Institutional Yield Vector Map", fill=(71, 85, 105), font=math_equation_font)
    
    # MIDDLE LEFT BLOCKS
    draw.text((left_margin, 370), "[BOARD RESULT MODEL]", fill=(100, 116, 139), font=small_label_font)
    draw.text((left_margin, 395), f"ρ (Consistency) ➔ {rho_stability}x Index", fill=TEXT_COLOR, font=small_label_font)
    draw.text((left_margin, 420), f"g (Growth Trend) ➔ +{round(growth_improvement, 1)}%", fill=ACENT_COLOR, font=math_notations_font)
    
    # BOTTOM LEFT BLOCKS
    draw.text((left_margin, 505), "[EDUCATION AUDIT RATIO]", fill=(100, 116, 139), font=small_label_font)
    draw.text((left_margin, 530), "Status ➔ PREDICTIVE BOARD PASS", fill=TEXT_COLOR, font=small_label_font)

    # --- 📊 ORIGINAL POSITIONING BAR CHART CORE ---
    bar_w, gap = 32, 20
    start_x = 425  
    base_y = 440   
    last_x, last_y = 0, 0
    years_labels = ["2023", "2024", "2025", "2026"]

    for i, h in enumerate(ACTUAL_DATA_POINTS):
        x1 = start_x + (i * (bar_w + gap))
        y1 = base_y - h
        x2 = x1 + bar_w
        
        draw.rectangle([x1, y1 + 10, x2, base_y], fill=(38, 50, 68))
        draw.ellipse([x1, y1, x2, y1 + 16], fill=ACENT_COLOR)
        
        display_pct = f"{raw_actuals[i]}%"
        draw.text((x1, y1 - 22), display_pct, fill=ACENT_COLOR, font=small_label_font)
        draw.text((x1 + 2, base_y + 8), years_labels[i], fill=(150, 160, 180), font=small_label_font)
        if i == len(ACTUAL_DATA_POINTS)-1: 
            last_x, last_y = x1 + (bar_w // 2), y1 + 8

    for j, h in enumerate(PREDICTIVE_DATA_POINTS):
        cx = start_x + ((len(ACTUAL_DATA_POINTS) + j) * (bar_w + gap)) + (bar_w // 2)
        cy = base_y - h
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=PREDICTIVE_COLOR)
        draw.line([(last_x, last_y), (cx, cy)], fill=PREDICTIVE_COLOR, width=2)
        if j == 0:
            draw.text((cx - 15, cy - 22), "Target ➔", fill=PREDICTIVE_COLOR, font=small_label_font)
        last_x, last_y = cx, cy

    # =========================================================================
    # 🎯 UPDATED: LAMBDA AREA (Shows Pona varuda centum count clearly)
    # =========================================================================
    draw.text((right_margin, 475), "[CENTUM YIELD ATTAINMENT]", fill=(100, 116, 139), font=small_label_font)
    draw.text((right_margin, 500), f"λ (2025 Centum) ➔ {past_year_centums} Students", fill=PREDICTIVE_COLOR, font=math_notations_font)
    draw.text((right_margin, 530), "Perfect Score Academic Value", fill=(71, 85, 105), font=math_equation_font)

    # =========================================================================
    # 📖 🏫 UPDATED: BOARD METRIC GLOSSARY BOX & TEXT WRAPPING 
    # =========================================================================
    box_x1, box_y1, box_x2, box_y2 = 105, 575, 515, 742
    draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline=(40, 52, 72), fill=(12, 18, 28), width=2)
    
    glossary_y = box_y1 + 8
    line_spacing = 14
    draw.text((box_x1 + 15, glossary_y), "BOARD PERFORMANCE METRICS GLOSSARY", fill=ACENT_COLOR, font=small_label_font)
    draw.text((box_x1 + 15, glossary_y + 18), f"g (Growth Trend) : Varuda Board Paritchai Vali Valarchiyin Alavu (+{round(growth_improvement, 1)}%)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + line_spacing), "β (Audit Status)  : Kalvi Thuraiyin Re-evaluation Criteria Matrum Stat", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 2)), f"α (Growth Index) : School Kalvi Nambikkai High-Performance Param ({alpha_trust}%)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 3)), f"ρ (Consistency)  : Maanavargal Board Paritchai Siraana Therchi Index", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 4)), f"λ (Centum Vector) : Pona Varudam (2025) Muzhu Madhipen Petra Maanavargal ({past_year_centums} Nos)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 5)), f"μ (Mean Pass)     : Cumulative Passing Strength of Registered Batches ({round(avg_pass, 1)}%)", fill=(148, 163, 184), font=glossary_font)

    # Footers
    draw.text((105, 755), f"SCHOOL BOARD IDENTITY CONTROLLER v3.2 - ID: {school_id}", fill=(100, 116, 139), font=small_label_font)

    # =========================================================================
    # 🛠️ QR POSITION & SCALE 
    # =========================================================================
    qr_url = "https://tnsevai.tn.gov.in/" if "GHS" in school_id.upper() or "GHSS" in school_id.upper() else "https://google.com"
    
    qr_gen = qrcode.QRCode(version=1, box_size=4, border=1)
    qr_gen.add_data(qr_url)
    qr_gen.make(fit=True)
    
    qr_img = qr_gen.make_image(fill_color="white", back_color=BG_COLOR).convert("RGBA")
    qw, qh = qr_img.size
    
    qr_target_x = SIZE[0] - qw - 105  
    qr_target_y = box_y1 + ((box_y2 - box_y1) - qh) // 2  
    
    image.paste(qr_img, (qr_target_x, qr_target_y), qr_img)
    # =========================================================================

    output_path = unique_output_path(output_dir, school_id)
    image.save(output_path, "PNG")
    if show_dialog:
        from tkinter import messagebox

        messagebox.showinfo("Success", f"Symmetrical Evaluation Matrix Vehicle Logo Generated!")
    return output_path


def generate_school(school_id, school_name, board_type, style, output_dir="generated/school"):
    return generate_school_logo(school_id, school_name, board_type, style, output_dir, show_dialog=False)

# --- Tkinter Application Engine Interface ---
def run_app():
    import tkinter as tk
    from tkinter import messagebox, ttk
    from PIL import ImageTk

    def on_generate():
        sch_id = e1.get().strip()
        name = e2.get().strip()
        board = board_combo.get()
        selected_font = font_var.get()
        if sch_id and name:
            filename = generate_school_logo(sch_id.upper(), name.upper(), board, selected_font)
            img_res = Image.open(filename)
            tk_img = ImageTk.PhotoImage(img_res.resize((480, 480)))
            canvas_label.config(image=tk_img)
            canvas_label.image = tk_img
        else:
            messagebox.showwarning("Input Error", "Please fill School Credentials properly.")

    root = tk.Tk()
    root.title("School Board Performance Identity Dashboard")
    root.geometry("560x860")
    root.configure(bg="#111517")

    tk.Label(root, text="School Registration Code / EMIS ID:", bg="#111517", fg="white", font=("Arial", 10)).pack(pady=5)
    e1 = tk.Entry(root, font=("Arial", 11), justify="center", width=25); e1.insert(0, "GHS-AVINASHI"); e1.pack()
    
    tk.Label(root, text="Display Branding School Name:", bg="#111517", fg="white", font=("Arial", 10)).pack(pady=5)
    e2 = tk.Entry(root, font=("Arial", 11), justify="center", width=25); e2.insert(0, "GHS AVINASHI"); e2.pack()

    tk.Label(root, text="Select Academic Evaluation Board Metric:", bg="#111517", fg="white", font=("Arial", 10)).pack(pady=5)
    board_combo = ttk.Combobox(root, values=["10th Board (SSLC)", "12th Board (HSC)"], state="readonly", font=("Arial", 10), justify="center")
    board_combo.set("10th Board (SSLC)")
    board_combo.pack(pady=3)

    tk.Label(root, text="Select Custom Typography Text Style:", bg="#111517", fg="#FF2884", font=("Arial", 10, "bold")).pack(pady=8)
    
    font_options = ["Classic Standard (Arial)", "Artistic Stylized (Gabriola)", "Cursive Script (Vladimir)", "Playful Stylized (Comic Bold)"]
    font_var = tk.StringVar(root)
    font_var.set(font_options[0]) 
    
    font_dropdown = tk.OptionMenu(root, font_var, *font_options)
    font_dropdown.config(font=("Arial", 10), bg="#1E293B", fg="white", activebackground="#334155")
    font_dropdown.pack(pady=5)

    btn = tk.Button(root, text="GENERATE PERFORMANCE LOGO", command=on_generate, bg="#FF2884", fg="white", font=("Arial", 11, "bold"), padx=10, pady=5)
    btn.pack(pady=15)

    canvas_label = tk.Label(root, bg="#111517")
    canvas_label.pack()

    root.mainloop()

if __name__ == "__main__":
    run_app()
