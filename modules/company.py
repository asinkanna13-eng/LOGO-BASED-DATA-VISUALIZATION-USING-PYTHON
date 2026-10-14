import math
import logging
import re

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
import yfinance as yf   # pyright: ignore[reportMissingImports]

from modules.output_utils import unique_output_path

logger = logging.getLogger(__name__)

# --- Configuration Section ---
SIZE = (800, 800)
BG_COLOR = (11, 15, 23)
PREDICTIVE_COLOR = (0, 176, 255) 
TEXT_COLOR = (255, 255, 255)

def get_live_company_growth(ticker_symbol):
    ticker = ticker_symbol.strip().upper()
    if not re.fullmatch(r"[A-Z0-9.^_-]{1,12}", ticker):
        raise ValueError("Enter a valid Yahoo Finance ticker symbol, such as AAPL.")

    try:
        logger.info("Fetching five years of Yahoo Finance history for %s", ticker)
        history = yf.Ticker(ticker).history(period="5y", timeout=15)
    except Exception as error:
        logger.exception("Yahoo Finance request failed for ticker %s", ticker)
        reason = f"{type(error).__name__} {error}".lower()
        if "timeout" in reason or "timed out" in reason:
            message = f"Yahoo Finance timed out while retrieving {ticker}. Please try again."
        elif any(term in reason for term in ("connection", "network", "curl")):
            message = f"Could not connect to Yahoo Finance for {ticker}. Check your internet connection and retry."
        else:
            message = f"Yahoo Finance could not retrieve live market data for {ticker}. Check the ticker and try again."
        raise ValueError(message) from error

    if not isinstance(history, pd.DataFrame):
        logger.error("Yahoo Finance returned a non-DataFrame response for ticker %s: %s", ticker, type(history).__name__)
        raise ValueError(f"Yahoo Finance returned an unexpected response for {ticker}.")
    if history.empty:
        logger.warning("Yahoo Finance returned no history for ticker %s", ticker)
        raise ValueError(f"Yahoo Finance returned no market history for {ticker}. Verify the ticker symbol.")
    if "Close" not in history.columns:
        logger.error("Yahoo Finance history for %s is missing its Close column: %s", ticker, list(history.columns))
        raise ValueError(f"Yahoo Finance returned data without the required Close price column for {ticker}.")

    try:
        close_prices = pd.to_numeric(history["Close"], errors="coerce").dropna()
        if not isinstance(close_prices.index, pd.DatetimeIndex):
            raise TypeError("The Close price data does not have a date index.")
        yearly_avg = close_prices.resample("YE").mean().dropna().tail(5)
    except (TypeError, ValueError) as error:
        logger.exception("Yahoo Finance returned unusable Close data for ticker %s", ticker)
        raise ValueError(f"Yahoo Finance returned market data in an unexpected format for {ticker}.") from error

    if len(yearly_avg) < 4:
        logger.warning("Yahoo Finance returned only %s annual values for %s", len(yearly_avg), ticker)
        raise ValueError(f"Yahoo Finance returned fewer than four years of price history for {ticker}.")

    actuals = yearly_avg.iloc[:4].astype(float).tolist()
    predictive = [yearly_avg.iloc[3] * 1.12, yearly_avg.iloc[3] * 1.25]
    if not all(math.isfinite(value) for value in (*actuals, *predictive)):
        logger.error("Yahoo Finance returned non-finite price values for ticker %s", ticker)
        raise ValueError(f"Yahoo Finance returned invalid price values for {ticker}.")
    return actuals, predictive

def draw_hexagon(draw, center, size, color, width=1):
    points = []
    for i in range(6):
        angle = math.radians(60 * i)
        px = center[0] + size * math.cos(angle)
        py = center[1] + size * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, outline=color, width=width)

def generate_company(ticker_symbol, company_name, font_selection, output_dir="generated/company", show_dialog=True):
    raw_actuals, raw_predicts = get_live_company_growth(ticker_symbol)
    
    # Normalization Scaling (Restoring original bar height ranges)
    all_vals = raw_actuals + raw_predicts
    min_v, max_v = min(all_vals), max(all_vals)
    span = (max_v - min_v) if max_v != min_v else 1
    
    ACTUAL_DATA_POINTS = [80 + ((v - min_v) / span) * 220 for v in raw_actuals]
    PREDICTIVE_DATA_POINTS = [80 + ((v - min_v) / span) * 220 for v in raw_predicts]

    total_summation_val = int(sum(raw_actuals) + sum(raw_predicts))

    if len(raw_actuals) >= 2 and raw_actuals[0] > 0 and raw_actuals[-2] != 0:
        cagr_rate = ((raw_actuals[-1] / raw_actuals[0]) ** (1/4) - 1) * 100
        risk_beta = max(0.5, min(2.0, 1 + (raw_actuals[-1] - raw_actuals[-2])/raw_actuals[-2]))
    else:
        cagr_rate = 0.0
        risk_beta = 1.0

    alpha_outperform = round(cagr_rate * 0.15, 2) 
    rho_liquidity = round(1.2 + (cagr_rate * 0.02), 2) 
    lambda_dominance = round(max(5.0, min(95.0, 45.0 + (cagr_rate * 1.2))), 1)

    if cagr_rate > 10:
        accent_color = (0, 255, 128) 
    elif cagr_rate < 0:
        accent_color = (255, 60, 60) 
    else:
        accent_color = (180, 210, 255) 

    ACENT_COLOR = accent_color 
    image = Image.new("RGBA", SIZE, BG_COLOR)
    draw = ImageDraw.Draw(image)

    # --- Safe Font Loader ---
    font_files = {
        "Artistic Stylized (Gabriola)": "C:\\Windows\\Fonts\\gabriola.ttf",
        "Cursive Script (Vladimir)": "C:\\Windows\\Fonts\\vladimir.ttf",
        "Playful Stylized (Comic Bold)": "C:\\Windows\\Fonts\\comicbd.ttf",
        "Classic Standard (Arial)": "C:\\Windows\\Fonts\\arialbd.ttf",
        "Serif": "C:\\Windows\\Fonts\\cambriab.ttf",
        "Sans Serif": "C:\\Windows\\Fonts\\arialbd.ttf",
        "Monospace": "C:\\Windows\\Fonts\\consolab.ttf",
    }
    CHOSEN_FONT_PATH = font_files.get(font_selection, "C:\\Windows\\Fonts\\gabriola.ttf")

    try:
        brand_giant_letter = ImageFont.truetype(CHOSEN_FONT_PATH, 180)
        brand_text_font = ImageFont.truetype(CHOSEN_FONT_PATH, 65)
        math_equation_font = ImageFont.truetype("C:\\Windows\\Fonts\\cambriab.ttf", 18) 
        math_notations_font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 22)
        small_label_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 14)
        glossary_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 11) 
    except IOError:
        try:
            brand_giant_letter = ImageFont.load_default(size=180)
            brand_text_font = ImageFont.load_default(size=65)
            math_equation_font = ImageFont.load_default(size=18)
            math_notations_font = ImageFont.load_default(size=22)
            small_label_font = ImageFont.load_default(size=14)
            glossary_font = ImageFont.load_default(size=11)
        except Exception:
            brand_giant_letter = brand_text_font = math_equation_font = ImageFont.load_default()
            math_notations_font = small_label_font = glossary_font = ImageFont.load_default()

    # Perfect Radiated Background Circle & Hexagon Systems
    center_canvas = (SIZE[0] // 2, SIZE[1] // 2)
    draw_hexagon(draw, center_canvas, 340, (30, 41, 59, 100), width=3)
    
    # Accurate Radius bounding box calculation for flawless circle
    circle_radius = 338
    circle_box = [center_canvas[0]-circle_radius, center_canvas[1]-circle_radius, center_canvas[0]+circle_radius, center_canvas[1]+circle_radius]
    draw.ellipse(circle_box, outline=(255, 255, 255, 12), width=2)

    # 🏢 BRAND CENTER CORE
    first_letter = company_name[0].upper() if company_name else "X"
    full_name = company_name.upper()
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
    draw.text((gw_x, brand_y_anchor - 25), first_letter, fill=(255, 255, 255, 12), font=brand_giant_letter)

    current_x = brand_x_centered
    for letter in full_name:
        text_color_pick = "white" if letter != first_letter else ACENT_COLOR
        draw.text((current_x, brand_y_anchor + 80), letter, fill=text_color_pick, font=brand_text_font)
        left, top, right, bottom = draw.textbbox((0, 0), letter, font=brand_text_font)
        current_x += (right - left) + letter_spacing_gap

    # =========================================================================
    # 📐 FIXED FINANCIAL COORDINATES SYSTEM (Aligned with Left and Right Flow)
    # =========================================================================
    
    # TOP LEFT & RIGHT BLOCKS
    draw.text((70, 65), "[MARKET BEAT THIRAN]", fill=(100, 116, 139), font=small_label_font)
    draw.text((70, 88), f"α (Alpha Share) ➔ +{alpha_outperform}%", fill=ACENT_COLOR, font=math_notations_font)
    draw.text((70, 118), "η Operational Efficiency Active", fill=(71, 85, 105), font=math_equation_font)
    
    draw.text((515, 65), "[TOTAL MARKET VALUE]", fill=(100, 116, 139), font=small_label_font)
    draw.text((515, 88), f"∑ Asset Pool = ${total_summation_val}", fill=ACENT_COLOR, font=math_notations_font)
    draw.text((515, 118), "∂ Dynamic Delta Drift Matrix", fill=(71, 85, 105), font=math_equation_font)
    
    # MIDDLE LEFT BLOCKS
    draw.text((70, 370), "[LIQUIDITY ENGINE]", fill=(100, 116, 139), font=small_label_font)
    draw.text((70, 395), f"ρ (Cash Ratio) ➔ {rho_liquidity}x Flow", fill=TEXT_COLOR, font=small_label_font)
    draw.text((70, 420), f"g (CAGR Rate) ➔ {round(cagr_rate, 1)}%", fill=ACENT_COLOR, font=math_notations_font)
    
    # BOTTOM LEFT BLOCKS
    draw.text((70, 505), "[RISK VOLATILITY PRO]", fill=(100, 116, 139), font=small_label_font)
    draw.text((70, 530), f"β (Beta Market Risk) = {round(risk_beta, 2)}", fill=TEXT_COLOR, font=small_label_font)

    # --- 📊 ORIGINAL POSITIONING BAR CHART CORE (FIRST UNTOUCHED POSITION) ---
    bar_w, gap = 38, 24
    start_x = 440  
    base_y = 440   # Restored original base height coordinate profile
    last_x, last_y = 0, 0

    for i, h in enumerate(ACTUAL_DATA_POINTS):
        x1 = start_x + (i * (bar_w + gap))
        y1 = base_y - h
        x2 = x1 + bar_w
        
        draw.rectangle([x1, y1 + 10, x2, base_y], fill=(30, 41, 59))
        draw.ellipse([x1, y1, x2, y1 + 16], fill=ACENT_COLOR)
        
        display_price = f"${int(raw_actuals[i])}"
        draw.text((x1, y1 - 22), display_price, fill=ACENT_COLOR, font=small_label_font)
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
    draw.text((515, 475), "[MARKET DOMINANCE]", fill=(100, 116, 139), font=small_label_font)
    draw.text((515, 500), f"λ (Lambda) ➔ {lambda_dominance}% Share", fill=PREDICTIVE_COLOR, font=math_notations_font)
    draw.text((515, 530), "Sector Control Dominance Engine", fill=(71, 85, 105), font=math_equation_font)

    # =========================================================================
    # 📖 DYNAMIC EXPANDED GLOSSARY CONTAINER BOX (Y: 575 to 740)
    # =========================================================================
    box_x1, box_y1, box_x2, box_y2 = 70, 575, 535, 742
    draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline=(45, 55, 72), fill=(15, 23, 42), width=2)
    
    glossary_y = box_y1 + 8
    line_spacing = 14
    draw.text((box_x1 + 15, glossary_y), "ADVANCED FINANCIAL GLOSSARY INDEX", fill=ACENT_COLOR, font=small_label_font)
    draw.text((box_x1 + 15, glossary_y + 18), f"g (CAGR Rate)   : Valarchi Vegam (Asset Compounded Growth = {round(cagr_rate, 1)}%)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + line_spacing), f"β (Beta Risk)    : Abhaya Alavu (Market Correlation Risk Factor = {round(risk_beta, 2)})", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 2)), f"α (Alpha Gain)  : Santhai Jeyikkum Thiran (Market Outperformance = +{alpha_outperform}%)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 3)), f"ρ (Rho Flow)    : Kaiyilulla Cash Adhigaram (Corporate Liquidity Flow Ratio)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 4)), f"λ (Lambda Share): Santhai Aathikkam (Industry Sector Dominance = {lambda_dominance}%)", fill=(148, 163, 184), font=glossary_font)
    draw.text((box_x1 + 15, glossary_y + 18 + (line_spacing * 5)), "∑ (Summation)   : Motha Kootu Mathippu (Total Unified Five-Year Price Data)", fill=(148, 163, 184), font=glossary_font)

    # Absolute Bottom Footers
    draw.text((70, 755), f"FINANCIAL LOGO MATRIX v3.2 - TICKER: {ticker_symbol}", fill=(100, 116, 139), font=small_label_font)

    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(f"https://finance.yahoo.com/quote/{ticker_symbol}")
    qr_img = qr.make_image(fill_color="white", back_color=BG_COLOR).convert("RGBA")
    image.paste(qr_img, (SIZE[0]-qr_img.size[0]-70, SIZE[1]-qr_img.size[1]-60))

    output_path = unique_output_path(output_dir, ticker_symbol)
    image.save(output_path, "PNG")
    if show_dialog:
        from tkinter import messagebox

        messagebox.showinfo("Success", f"Symmetrical System Layout Reconfigured for {ticker_symbol}!")
    return output_path


def generate_math_logo(ticker_symbol, company_name, font_selection):
    return generate_company(ticker_symbol, company_name, font_selection)

# --- UI Framework (Tkinter) ---
def run_app():
    import tkinter as tk
    from tkinter import messagebox
    from PIL import ImageTk

    def on_generate():
        ticker = e1.get().strip()
        name = e2.get().strip()
        selected_font = font_var.get()
        if ticker and name:
            filename = generate_math_logo(ticker.upper(), name.upper(), selected_font)
            img_res = Image.open(filename)
            tk_img = ImageTk.PhotoImage(img_res.resize((480, 480)))
            canvas_label.config(image=tk_img)
            canvas_label.image = tk_img
        else:
            messagebox.showwarning("Input Error", "Please fill Ticker and Name properly.")

    root = tk.Tk()
    root.title("Advanced Mathematical Finance Matrix System")
    root.geometry("560x840")
    root.configure(bg="#111517")

    tk.Label(root, text="Brand Ticker Symbol (e.g. AAPL):", bg="#111517", fg="white", font=("Arial", 10)).pack(pady=5)
    e1 = tk.Entry(root, font=("Arial", 11), justify="center"); e1.insert(0, "AAPL"); e1.pack()
    
    tk.Label(root, text="Display Corporate Name (e.g. APPLE):", bg="#111517", fg="white", font=("Arial", 10)).pack(pady=5)
    e2 = tk.Entry(root, font=("Arial", 11), justify="center"); e2.insert(0, "APPLE"); e2.pack()

    tk.Label(root, text="Select Fancy Brand Text Style:", bg="#111517", fg="#00E676", font=("Arial", 10, "bold")).pack(pady=8)
    
    font_options = ["Artistic Stylized (Gabriola)", "Cursive Script (Vladimir)", "Playful Stylized (Comic Bold)", "Classic Standard (Arial)"]
    font_var = tk.StringVar(root)
    font_var.set(font_options[0]) 
    
    font_dropdown = tk.OptionMenu(root, font_var, *font_options)
    font_dropdown.config(font=("Arial", 10), bg="#1E293B", fg="white", activebackground="#334155")
    font_dropdown.pack(pady=5)

    btn = tk.Button(root, text="GENERATE MATH IDENTITY ENGINE", command=on_generate, bg="#00E676", fg="black", font=("Arial", 11, "bold"), padx=10, pady=5)
    btn.pack(pady=15)

    canvas_label = tk.Label(root, bg="#111517")
    canvas_label.pack()

    root.mainloop()

if __name__ == "__main__":
    run_app()
