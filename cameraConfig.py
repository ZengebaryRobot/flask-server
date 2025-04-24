import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests


camera1_ip = ""
camera2_ip = ""


def update_camera_settings(camera_url, settings):
    try:
        response = requests.get(camera_url, params=settings)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Camera settings updated successfully!")
        else:
            messagebox.showerror("Error", "Failed to update camera settings.")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")


def update_camera1():
    camera_url = f"http://{camera1_ip}/config"
    settings = {
        "framesize": framesize_var1.get(),
        "quality": quality_var1.get(),
        "brightness": brightness_var1.get(),
        "contrast": contrast_var1.get(),
        "saturation": saturation_var1.get(),
        "special_effect": special_effect_var1.get(),
        "awb": awb_var1.get(),
        "awb_gain": awb_gain_var1.get(),
        "wb_mode": wb_mode_var1.get(),
        "aec": aec_var1.get(),
        "aec2": aec2_var1.get(),
        "ae_level": ae_level_var1.get(),
        "aec_value": aec_value_var1.get(),
        "agc": agc_var1.get(),
        "gainceiling": gainceiling_var1.get(),
        "hmirror": hmirror_var1.get(),
        "vflip": vflip_var1.get(),
        "dcw": dcw_var1.get(),
        "colorbar": colorbar_var1.get(),
    }
    update_camera_settings(camera_url, settings)


def update_camera2():
    camera_url = f"http://{camera2_ip}/config"
    settings = {
        "framesize": framesize_var2.get(),
        "quality": quality_var2.get(),
        "brightness": brightness_var2.get(),
        "contrast": contrast_var2.get(),
        "saturation": saturation_var2.get(),
        "special_effect": special_effect_var2.get(),
        "awb": awb_var2.get(),
        "awb_gain": awb_gain_var2.get(),
        "wb_mode": wb_mode_var2.get(),
        "aec": aec_var2.get(),
        "aec2": aec2_var2.get(),
        "ae_level": ae_level_var2.get(),
        "aec_value": aec_value_var2.get(),
        "agc": agc_var2.get(),
        "gainceiling": gainceiling_var2.get(),
        "hmirror": hmirror_var2.get(),
        "vflip": vflip_var2.get(),
        "dcw": dcw_var2.get(),
        "colorbar": colorbar_var2.get(),
    }
    update_camera_settings(camera_url, settings)


def set_ips():
    global camera1_ip, camera2_ip
    camera1_ip = ip_entry1.get()
    camera2_ip = ip_entry2.get()

    if not camera1_ip or not camera2_ip:
        messagebox.showerror("Error", "Please enter both IP addresses!")
        return

    ip_frame.grid_forget()
    camera1_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
    camera2_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
    adjust_window_size()


def adjust_window_size():
    root.update_idletasks()
    bbox = canvas.bbox("all")
    width = bbox[2] - bbox[0] + 20
    height = bbox[3] - bbox[1] + 20
    width += scrollbar.winfo_width() + 20
    height = min(height, 700)
    root.minsize(400, 300)
    root.geometry(f"{width}x{height}")


root = tk.Tk()
root.title("ESP32 Camera Configuration")
root.configure(bg="#f0f2f5")


style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TLabel", font=("Segoe UI", 10), background="#f0f2f5", foreground="#333"
)
style.configure(
    "TButton",
    font=("Segoe UI", 10, "bold"),
    padding=8,
    background="#007bff",
    foreground="#ffffff",
)
style.map("TButton", background=[("active", "#0056b3")])
style.configure("TFrame", background="#f0f2f5")
style.configure("Card.TFrame", background="#ffffff", relief="flat")
style.configure("Card.TLabelframe", background="#ffffff", relief="flat")
style.configure(
    "Card.TLabelframe.Label",
    font=("Segoe UI", 12, "bold"),
    background="#ffffff",
    foreground="#333",
)
style.configure(
    "TCheckbutton", font=("Segoe UI", 10), background="#ffffff", foreground="#333"
)
style.configure("TCombobox", font=("Segoe UI", 10), padding=5)
style.map(
    "TCombobox",
    fieldbackground=[("readonly", "#ffffff")],
    foreground=[("readonly", "#333")],
)
style.configure("Horizontal.TScale", background="#ffffff")


framesize_var1 = tk.StringVar(value="QVGA")
quality_var1 = tk.IntVar(value=10)
brightness_var1 = tk.IntVar(value=0)
contrast_var1 = tk.IntVar(value=0)
saturation_var1 = tk.IntVar(value=0)
special_effect_var1 = tk.StringVar(value="0")
awb_var1 = tk.BooleanVar(value=True)
awb_gain_var1 = tk.BooleanVar(value=True)
wb_mode_var1 = tk.StringVar(value="0")
aec_var1 = tk.BooleanVar(value=True)
aec2_var1 = tk.BooleanVar(value=True)
ae_level_var1 = tk.IntVar(value=0)
aec_value_var1 = tk.IntVar(value=204)
agc_var1 = tk.BooleanVar(value=True)
gainceiling_var1 = tk.IntVar(value=0)
hmirror_var1 = tk.BooleanVar(value=False)
vflip_var1 = tk.BooleanVar(value=False)
dcw_var1 = tk.BooleanVar(value=True)
colorbar_var1 = tk.BooleanVar(value=False)

framesize_var2 = tk.StringVar(value="QVGA")
quality_var2 = tk.IntVar(value=10)
brightness_var2 = tk.IntVar(value=0)
contrast_var2 = tk.IntVar(value=0)
saturation_var2 = tk.IntVar(value=0)
special_effect_var2 = tk.StringVar(value="0")
awb_var2 = tk.BooleanVar(value=True)
awb_gain_var2 = tk.BooleanVar(value=True)
wb_mode_var2 = tk.StringVar(value="0")
aec_var2 = tk.BooleanVar(value=True)
aec2_var2 = tk.BooleanVar(value=True)
ae_level_var2 = tk.IntVar(value=0)
aec_value_var2 = tk.IntVar(value=204)
agc_var2 = tk.BooleanVar(value=True)
gainceiling_var2 = tk.IntVar(value=0)
hmirror_var2 = tk.BooleanVar(value=False)
vflip_var2 = tk.BooleanVar(value=False)
dcw_var2 = tk.BooleanVar(value=True)
colorbar_var2 = tk.BooleanVar(value=False)


def add_labeled_slider(parent, label_text, variable, min_val, max_val, row):
    frame = ttk.Frame(parent, style="Card.TFrame")
    frame.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    ttk.Label(frame, text=label_text, style="TLabel").pack(side="left", padx=5)
    slider = ttk.Scale(
        frame, variable=variable, from_=min_val, to=max_val, orient="horizontal"
    )
    slider.pack(side="left", fill="x", expand=True, padx=5)
    value_label = ttk.Label(frame, text=f"{variable.get()}", style="TLabel")
    value_label.pack(side="right", padx=5)
    variable.trace("w", lambda *args: value_label.configure(text=f"{variable.get()}"))


def add_labeled_dropdown(parent, label_text, variable, options, row):
    frame = ttk.Frame(parent, style="Card.TFrame")
    frame.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    ttk.Label(frame, text=label_text, style="TLabel").pack(side="left", padx=5)
    dropdown = ttk.Combobox(
        frame, textvariable=variable, values=options, state="readonly", width=15
    )
    dropdown.pack(side="left", padx=5)


main_frame = ttk.Frame(root, style="TFrame")
main_frame.pack(expand=True, fill="both", padx=20, pady=20)


canvas = tk.Canvas(main_frame, bg="#f0f2f5", highlightthickness=0)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

scrollable_frame = ttk.Frame(canvas, style="TFrame")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")


header_frame = ttk.Frame(scrollable_frame, style="TFrame")
header_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
ttk.Label(
    header_frame,
    text="ESP32 Camera Configuration",
    font=("Segoe UI", 16, "bold"),
    style="TLabel",
).pack()


ip_frame = ttk.Frame(scrollable_frame, style="Card.TFrame")
ip_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
ip_frame.configure(relief="flat", padding=15)

ttk.Label(ip_frame, text="Camera 1 IP:", style="TLabel").grid(
    row=0, column=0, padx=10, pady=5, sticky="w"
)
ip_entry1 = ttk.Entry(ip_frame, width=20, font=("Segoe UI", 10))
ip_entry1.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(ip_frame, text="Camera 2 IP:", style="TLabel").grid(
    row=1, column=0, padx=10, pady=5, sticky="w"
)
ip_entry2 = ttk.Entry(ip_frame, width=20, font=("Segoe UI", 10))
ip_entry2.grid(row=1, column=1, padx=10, pady=5)

start_button = ttk.Button(ip_frame, text="⚙ Set IPs", command=set_ips, style="TButton")
start_button.grid(row=2, column=0, columnspan=2, pady=10)


camera1_frame = ttk.LabelFrame(
    scrollable_frame, text="Camera 1 Settings", style="Card.TLabelframe"
)
camera1_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
camera1_frame.grid_forget()


camera2_frame = ttk.LabelFrame(
    scrollable_frame, text="Camera 2 Settings", style="Card.TLabelframe"
)
camera2_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
camera2_frame.grid_forget()


add_labeled_dropdown(
    camera1_frame,
    "Resolution",
    framesize_var1,
    ["UXGA", "SXGA", "XGA", "SVGA", "VGA"],
    0,
)
add_labeled_slider(camera1_frame, "Quality", quality_var1, 10, 63, 1)
add_labeled_slider(camera1_frame, "Brightness", brightness_var1, -2, 2, 2)
add_labeled_slider(camera1_frame, "Contrast", contrast_var1, -2, 2, 3)
add_labeled_slider(camera1_frame, "Saturation", saturation_var1, -2, 2, 4)
add_labeled_dropdown(
    camera1_frame,
    "Special Effect",
    special_effect_var1,
    [
        "No Effect",
        "Negative",
        "Grayscale",
        "Red Tint",
        "Green Tint",
        "Blue Tint",
        "Sepia",
    ],
    5,
)


check_frame1 = ttk.Frame(camera1_frame, style="Card.TFrame")
check_frame1.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
ttk.Checkbutton(check_frame1, text="AWB", variable=awb_var1, style="TCheckbutton").grid(
    row=0, column=0, padx=10, pady=5, sticky="w"
)
ttk.Checkbutton(
    check_frame1, text="AWB Gain", variable=awb_gain_var1, style="TCheckbutton"
).grid(row=0, column=1, padx=10, pady=5, sticky="w")
ttk.Checkbutton(check_frame1, text="AEC", variable=aec_var1, style="TCheckbutton").grid(
    row=1, column=0, padx=10, pady=5, sticky="w"
)
ttk.Checkbutton(
    check_frame1, text="AEC2", variable=aec2_var1, style="TCheckbutton"
).grid(row=1, column=1, padx=10, pady=5, sticky="w")

add_labeled_dropdown(
    camera1_frame,
    "WB Mode",
    wb_mode_var1,
    ["Auto", "Sunny", "Cloudy", "Office", "Home"],
    7,
)
update_button1 = ttk.Button(
    camera1_frame, text="⬆ Update Camera 1", command=update_camera1, style="TButton"
)
update_button1.grid(row=8, column=0, columnspan=2, pady=10)


add_labeled_dropdown(
    camera2_frame,
    "Resolution",
    framesize_var2,
    ["UXGA", "SXGA", "XGA", "SVGA", "VGA"],
    0,
)
add_labeled_slider(camera2_frame, "Quality", quality_var2, 10, 63, 1)
add_labeled_slider(camera2_frame, "Brightness", brightness_var2, -2, 2, 2)
add_labeled_slider(camera2_frame, "Contrast", contrast_var2, -2, 2, 3)
add_labeled_slider(camera2_frame, "Saturation", saturation_var2, -2, 2, 4)
add_labeled_dropdown(
    camera2_frame,
    "Special Effect",
    special_effect_var2,
    [
        "No Effect",
        "Negative",
        "Grayscale",
        "Red Tint",
        "Green Tint",
        "Blue Tint",
        "Sepia",
    ],
    5,
)


check_frame2 = ttk.Frame(camera2_frame, style="Card.TFrame")
check_frame2.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
ttk.Checkbutton(check_frame2, text="AWB", variable=awb_var2, style="TCheckbutton").grid(
    row=0, column=0, padx=10, pady=5, sticky="w"
)
ttk.Checkbutton(
    check_frame2, text="AWB Gain", variable=awb_gain_var2, style="TCheckbutton"
).grid(row=0, column=1, padx=10, pady=5, sticky="w")
ttk.Checkbutton(check_frame2, text="AEC", variable=aec_var2, style="TCheckbutton").grid(
    row=1, column=0, padx=10, pady=5, sticky="w"
)
ttk.Checkbutton(
    check_frame2, text="AEC2", variable=aec2_var2, style="TCheckbutton"
).grid(row=1, column=1, padx=10, pady=5, sticky="w")

add_labeled_dropdown(
    camera2_frame,
    "WB Mode",
    wb_mode_var2,
    ["Auto", "Sunny", "Cloudy", "Office", "Home"],
    7,
)
update_button2 = ttk.Button(
    camera2_frame, text="⬆ Update Camera 2", command=update_camera2, style="TButton"
)
update_button2.grid(row=8, column=0, columnspan=2, pady=10)


scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
root.after(100, adjust_window_size)


def on_mouse_wheel(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")


canvas.bind_all("<MouseWheel>", on_mouse_wheel)

root.mainloop()
