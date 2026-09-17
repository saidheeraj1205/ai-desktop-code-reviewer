import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import keyboard
from openai import OpenAI
from PIL import Image, ImageDraw
import pystray

# ==========================================
# 1. CONFIGURATION
# ==========================================
OPENAI_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
AI_MODEL = "openai/gpt-oss-20b"  # Or your active Groq model name

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Global toggle state
is_active = True

# ==========================================
# 2. UI REVIEW DIALOG (Tkinter)
# ==========================================
class ReviewResultWindow:
    def __init__(self, original_code, review_text, fix_code):
        self.original_code = original_code
        self.fix_code = fix_code
        
        self.root = tk.Tk()
        self.root.title("🛡️ AI Code Reviewer")
        self.root.geometry("650x550")
        self.root.attributes('-topmost', True)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(header_frame, text="AI Code Review & Analysis", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        review_frame = ttk.Frame(notebook, padding=10)
        notebook.add(review_frame, text=" Analysis ")
        review_text_widget = tk.Text(review_frame, wrap="word", font=("Consolas", 10))
        review_text_widget.insert("1.0", review_text)
        review_text_widget.config(state="disabled")
        review_text_widget.pack(fill="both", expand=True)

        fix_frame = ttk.Frame(notebook, padding=10)
        notebook.add(fix_frame, text=" Suggested Fix ")
        fix_text_widget = tk.Text(fix_frame, wrap="none", font=("Consolas", 10), bg="#f4f4f4")
        fix_text_widget.insert("1.0", self.fix_code if self.fix_code else "No code fix needed.")
        fix_text_widget.pack(fill="both", expand=True)

        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.grid(row=2, column=0, sticky="ew")

        if self.fix_code:
            ttk.Button(button_frame, text="⚡ Replace Highlighted Code", command=self.replace_code).pack(side="right", padx=5)
            ttk.Button(button_frame, text="📋 Copy Fix", command=self.copy_fix).pack(side="right", padx=5)

        ttk.Button(button_frame, text="Close", command=self.root.destroy).pack(side="left", padx=5)
        self.root.mainloop()

    def copy_fix(self):
        pyperclip.copy(self.fix_code)
        messagebox.showinfo("Success", "Copied to clipboard!")

    def replace_code(self):
        pyperclip.copy(self.fix_code)
        self.root.destroy()
        time.sleep(0.1)
        keyboard.send('ctrl+v')

# ==========================================
# 3. CORE LOGIC
# ==========================================
is_processing = False  # <--- Added to prevent blank windows

def process_code_review():
    global is_active, is_processing
    
    # If paused or already reviewing, ignore the hotkey
    if not is_active or is_processing:
        return  

    is_processing = True
    try:
        # Wait 0.25s for your fingers to release the 'r' key!
        time.sleep(0.25)
        
        keyboard.send('ctrl+c')
        time.sleep(0.3)
        
        code_snippet = pyperclip.paste()
        if not code_snippet or not code_snippet.strip():
            return

        prompt = f"""
        You are an expert AI security engineer and code auditor.
        Identify bugs, security flaws, or bad practices.
        
        Return response in 2 sections separated by "---FIX_START---":
        1. Markdown analysis explanation.
        2. Exact corrected code block ONLY.

        Code:
        {code_snippet}
        """

        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        full_response = response.choices[0].message.content

        if "---FIX_START---" in full_response:
            parts = full_response.split("---FIX_START---")
            explanation = parts[0].strip()
            fix_code = parts[1].strip()
            
            # Clean up markdown backticks so they don't paste into your code
            if fix_code.startswith("```"):
                fix_code = "\n".join(fix_code.split("\n")[1:])
            if fix_code.endswith("```"):
                fix_code = "\n".join(fix_code.split("\n")[:-1])
            fix_code = fix_code.strip()
        else:
            explanation = full_response.strip()
            fix_code = ""

        ReviewResultWindow(code_snippet, explanation, fix_code)

    except Exception as e:
        messagebox.showerror("AI Review Error", f"Error during review:\n{e}")
    finally:
        # Unlock the process so you can run it again later
        is_processing = False

# ==========================================
# 4. SYSTEM TRAY & TOGGLE CONTROL
# ==========================================
def create_tray_icon():
    global is_active

    # Create Green / Red status icons dynamically
    def create_image(color):
        img = Image.new('RGB', (64, 64), color=(30, 30, 30))
        dc = ImageDraw.Draw(img)
        dc.ellipse([12, 12, 52, 52], fill=color)
        return img

    icon_green = create_image((40, 200, 40))   # Green = Running
    icon_red = create_image((220, 50, 50))     # Red = Stopped

    def toggle_status(icon, item):
        global is_active
        is_active = not is_active
        if is_active:
            icon.icon = icon_green
            icon.title = "AI Reviewer: RUNNING (Ctrl+Alt+R)"
        else:
            icon.icon = icon_red
            icon.title = "AI Reviewer: PAUSED"

    def get_status_text(item):
        return "🟢 Status: ACTIVE (Click to Stop)" if is_active else "🔴 Status: PAUSED (Click to Start)"

    def on_exit(icon, item):
        icon.stop()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem(get_status_text, toggle_status),
        pystray.MenuItem("Exit Completely", on_exit)
    )

    icon = pystray.Icon("AICodeReviewer", icon_green, "AI Reviewer: RUNNING (Ctrl+Alt+R)", menu)
    icon.run()

if __name__ == "__main__":
    keyboard.add_hotkey(
        'ctrl+alt+r', 
        lambda: threading.Thread(target=process_code_review).start(), 
        suppress=True  # <--- ADD THIS: Stops Windows from typing 'r' into the text box
    )
    create_tray_icon()