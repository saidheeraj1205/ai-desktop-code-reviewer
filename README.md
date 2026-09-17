# AI Desktop Code Reviewer

A lightweight, universal OS-level background utility that reviews and fixes code on-demand across *any* application using a global hotkey and high-speed Groq LLMs.

## 📌 About the Project

* **What the project is:** A silent desktop background utility that audits code security and logic bugs in real-time.
* **Why you built it:** To eliminate the friction of switching context, opening web browsers, or dealing with heavy IDE plugins just to get a quick code review.
* **What problem it solves:** Instantly identifies vulnerabilities (like SQL injection, XSS, resource leaks) and bad practices anywhere on your screen and patches them with a single click.
* **Who can use it:** Software developers, security engineers, students, and anyone writing code who wants instant AI feedback.

## ✨ Features

* **Universal Global Hotkey (`Ctrl + Alt + R`):** Highlight code anywhere and trigger an instant audit.
* **System Tray Integration:** Runs quietly in the background with a system tray icon featuring a live Start/Pause toggle.
* **1-Click Code Replacement:** Overwrite messy or vulnerable code automatically with production-ready fixes.
* **Debounced Execution:** Prevents multi-triggering, threading freezes, and "ghost" UI windows.
* **Windowless Execution (`.pyw`):** Runs seamlessly without ever showing a black command prompt window.
* **Markdown Sanitization:** Automatically strips markdown code-block wrappers to keep code insertions pure and executable.

## 🛠️ Technologies Used

* Python 3.x
* Groq API (OpenAI SDK wrapper routing to open-source LLMs)
* Tkinter (Actionable UI dialogs and tabbed windows)
* Pystray & Pillow (System tray management and dynamic icons)
* Keyboard & Pyperclip (OS-level global hotkey hooks and clipboard sync)

## 📂 Project Structure

```text
ai-desktop-code-reviewer/
│
├── ai_code_reviewer.pyw   # Main background utility script
├── .gitignore             # Git exclusion rules
└── README.md              # Project documentation