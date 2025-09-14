import tkinter as tk
from tkinter import messagebox, font
import random
import sys

# Try to initialize pygame mixer for optional sounds (silent if unavailable)
try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False


class KBCGame:
    def __init__(self):
        # --- Root window ---
        self.root = tk.Tk()
        self.root.title("Kaun Banega Crorepati - Live Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#0A0A2E")
        
        # Allow resizing to let maximize/restore work
        self.root.resizable(True, True)

        # Fullscreen toggle
        self.fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # Keyboard shortcuts for options and lifelines
        self.root.bind("a", lambda e: self.key_select(0))
        self.root.bind("A", lambda e: self.key_select(0))
        self.root.bind("b", lambda e: self.key_select(1))
        self.root.bind("B", lambda e: self.key_select(1))
        self.root.bind("c", lambda e: self.key_select(2))
        self.root.bind("C", lambda e: self.key_select(2))
        self.root.bind("d", lambda e: self.key_select(3))
        self.root.bind("D", lambda e: self.key_select(3))
        self.root.bind("<Return>", lambda e: self.lock_answer())
        self.root.bind("1", lambda e: self.use_5050())
        self.root.bind("2", lambda e: self.use_audience_poll())
        self.root.bind("3", lambda e: self.use_phone_friend())

        # Game state
        self.current_question = 0  # zero-based index
        self.score = 0
        self.lifelines_used = {"50_50": False, "audience": False, "phone": False}
        self.selected_option = None
        self.answer_locked = False
        self.awaiting_confirmation = False

        # Timer state (using after to avoid blocking)
        self.time_limit = 30
        self.time_left = self.time_limit
        self.timer_id = None
        self.timer_running = False

        # Host dialogue system
        self.host_messages = {
            'welcome': [
                "Namaste! Main hoon Amitabh Bachchan aur aap dekh rahe hain...",
                "KAUN BANEGA CROREPATI!",
                "Aaj humara contestant 1 crore jeetne ki koshish karega!"
            ],
            'question_intro': [
                "Chaliye dekhte hain aapka agla sawal...",
                "Yeh sawal hai {amount} rupaye ke liye...",
                "Dhyan se sochiye, samay simit hai!"
            ],
            'correct': [
                "Bilkul sahi jawab! Shabash!",
                "Excellent! Aap {amount} jeet gaye!",
                "Bahut khushi ki baat hai!"
            ],
            'wrong': [
                "Afsos! Yeh galat jawab hai.",
                "Sahi jawab tha {correct_option}.",
                "Koi baat nahi, aapne achha khela!"
            ],
            'lifeline': [
                "Lifeline ka istemaal karna chahte hain?",
                "Samajhdari ki baat hai!",
                "Chaliye dekhte hain kya milta hai!"
            ],
            'final': [
                "Yeh hai aapka 1 crore ka sawal!",
                "Sochiye... computer ji, lock kiya jaye?"
            ]
        }

        # Questions: improved / varied
        self.questions = [
            {
                "question": "Which programming language is considered the language of the web for front-end development?",
                "options": ["Python", "C++", "JavaScript", "Ruby"],
                "correct": 2,
                "category": "Technology",
            },
            {
                "question": "Vatican City is the smallest country in the world by area. Which continent is it located in?",
                "options": ["Asia", "Europe", "Africa", "South America"],
                "correct": 1,
                "category": "Geography",
            },
            {
                "question": "Which animal is the fastest land animal?",
                "options": ["Cheetah", "Pronghorn", "Lion", "Horse"],
                "correct": 0,
                "category": "Biology",
            },
            {
                "question": "Who proposed the theory of general relativity?",
                "options": ["Isaac Newton", "Albert Einstein", "Galileo Galilei", "Niels Bohr"],
                "correct": 1,
                "category": "Science",
            },
            {
                "question": "Which planet in our solar system has the most known moons (as of recent counts)?",
                "options": ["Earth", "Mars", "Saturn", "Mercury"],
                "correct": 2,
                "category": "Astronomy",
            },
            {
                "question": "What is the chemical symbol for silver?",
                "options": ["Ag", "Au", "Si", "Sr"],
                "correct": 0,
                "category": "Chemistry",
            },
            {
                "question": "Which author wrote the 'Harry Potter' series?",
                "options": ["J.K. Rowling", "C.S. Lewis", "Roald Dahl", "Stephen King"],
                "correct": 0,
                "category": "Literature",
            },
            {
                "question": "Which ancient civilization is credited with inventing paper?",
                "options": ["Egyptians", "Chinese", "Greeks", "Romans"],
                "correct": 1,
                "category": "History",
            },
            {
                "question": "Which fruit is considered the national fruit of Pakistan?",
                "options": ["Mango", "Banana", "Apple", "Pomegranate"],
                "correct": 0,
                "category": "General Knowledge",
            },
            {
                "question": "What is the longest bone in the human body?",
                "options": ["Femur", "Humerus", "Tibia", "Fibula"],
                "correct": 0,
                "category": "Biology",
            },
            {
                "question": "Which element has the symbol 'O'?",
                "options": ["Oxygen", "Osmium", "Gold", "Oganesson"],
                "correct": 0,
                "category": "Chemistry",
            },
            {
                "question": "Which is the largest desert on Earth by area?",
                "options": ["Sahara", "Gobi", "Antarctic Desert", "Arabian Desert"],
                "correct": 2,
                "category": "Geography",
            },
            {
                "question": "Which sport is often called the 'king of sports' worldwide?",
                "options": ["Cricket", "Tennis", "Football (Soccer)", "Basketball"],
                "correct": 2,
                "category": "Sports",
            },
            {
                "question": "Who painted 'The Starry Night'?",
                "options": ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Claude Monet"],
                "correct": 2,
                "category": "Art",
            },
            {
                "question": "At what Celsius temperature does water freeze at standard pressure?",
                "options": ["0°C", "100°C", "32°C", "-10°C"],
                "correct": 0,
                "category": "Science",
            },
        ]

        # Prize ladder (15 steps)
        self.prize_money = [
            "₹1,000",
            "₹2,000",
            "₹3,000",
            "₹5,000",
            "₹10,000",
            "₹20,000",
            "₹40,000",
            "₹80,000",
            "₹1,60,000",
            "₹3,20,000",
            "₹6,40,000",
            "₹12,50,000",
            "₹25,00,000",
            "₹50,00,000",
            "₹1 CRORE",
        ]
        # safe havens (zero-based indices)
        self.safe_havens = [4, 9, 14]  # after question 5,10,15 (indices 4,9,14)

        random.shuffle(self.questions)

        # Fonts
        self.title_font = font.Font(family="Arial", size=28, weight="bold")
        self.question_font = font.Font(family="Arial", size=16, weight="bold")
        self.option_font = font.Font(family="Arial", size=13, weight="bold")
        self.money_font = font.Font(family="Arial", size=10, weight="bold")
        self.host_font = font.Font(family="Arial", size=14, weight="bold")

        # Build UI
        self.setup_ui()
        self.show_welcome_screen()

    # ---------------------
    # Window behavior
    # ---------------------
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def exit_fullscreen(self, event=None):
        self.fullscreen = False
        self.root.attributes("-fullscreen", False)

    # ---------------------
    # Host System
    # ---------------------
    def show_host_message(self, message_type, **kwargs):
        """Display host message in the dedicated host area"""
        if hasattr(self, 'host_label'):
            messages = self.host_messages.get(message_type, ["..."])
            if message_type == 'question_intro':
                current_amount = self.prize_money[self.current_question]
                message = random.choice(messages).format(amount=current_amount)
            elif message_type == 'correct':
                current_amount = self.prize_money[self.current_question]
                message = random.choice(messages).format(amount=current_amount)
            elif message_type == 'wrong':
                correct_option = chr(65 + self.questions[self.current_question]['correct'])
                message = random.choice(messages).format(correct_option=correct_option)
            else:
                message = random.choice(messages)
            
            self.host_label.config(text=f"🎤 Amitabh Bachchan: {message}")
            # Auto clear after some time for most messages
            if message_type not in ['welcome']:
                self.root.after(4000, lambda: self.clear_host_message())

    def clear_host_message(self):
        if hasattr(self, 'host_label'):
            self.host_label.config(text="🎤 Amitabh Bachchan: Sochiye... samay ja raha hai!")

    # ---------------------
    # UI Setup
    # ---------------------
    def setup_ui(self):
        # Main container with animated background
        self.main_frame = tk.Frame(self.root, bg="#0A0A2E")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add some visual effects
        self.create_animated_background()

    def create_animated_background(self):
        """Create animated background elements"""
        # Create canvas for background effects
        self.bg_canvas = tk.Canvas(self.main_frame, bg="#0A0A2E", highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Add some moving elements
        self.animate_background()

    def animate_background(self):
        """Simple background animation"""
        try:
            self.bg_canvas.delete("bg_effects")
            width = self.bg_canvas.winfo_width() if self.bg_canvas.winfo_width() > 1 else 1400
            height = self.bg_canvas.winfo_height() if self.bg_canvas.winfo_height() > 1 else 900
            
            # Create some glowing circles
            for i in range(3):
                x = (width * (i + 1)) // 4
                y = height // 2
                radius = 50 + (i * 20)
                color_intensity = abs(int(50 * (1 + 0.3 * ((self.current_question % 10) - 5))))
                color = f"#{color_intensity:02x}{color_intensity//2:02x}{min(100, color_intensity+50):02x}"
                
                self.bg_canvas.create_oval(
                    x - radius, y - radius, x + radius, y + radius,
                    fill="", outline=color, width=2, tags="bg_effects"
                )
            
            # Schedule next animation frame
            self.root.after(2000, self.animate_background)
        except:
            pass

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            if widget != self.bg_canvas:
                widget.destroy()

    # ---------------------
    # Welcome / Rules
    # ---------------------
    def show_welcome_screen(self):
        self.clear_screen()
        wf = tk.Frame(self.main_frame, bg="#0A0A2E")
        wf.pack(fill=tk.BOTH, expand=True)

        # Animated title
        title_frame = tk.Frame(wf, bg="#FFD700", bd=5, relief=tk.RAISED)
        title_frame.pack(pady=40)
        
        title_label = tk.Label(
            title_frame,
            text="KAUN BANEGA CROREPATI",
            font=self.title_font,
            bg="#FFD700",
            fg="#0A0A2E",
            padx=50,
            pady=25,
        )
        title_label.pack()
        
        # Add blinking effect to title
        self.animate_title(title_label)

        tk.Label(
            wf,
            text="🎬 LIVE EDITION 🎬",
            font=font.Font(size=18, weight="bold"),
            bg="#0A0A2E",
            fg="#FFD700",
        ).pack(pady=5)

        # Host introduction
        host_frame = tk.Frame(wf, bg="#1a1a4a", relief=tk.RAISED, bd=3)
        host_frame.pack(pady=20, padx=50, fill=tk.X)
        
        tk.Label(
            host_frame,
            text="🎤 Hosted by: Amitabh Bachchan",
            font=font.Font(size=16, weight="bold"),
            bg="#1a1a4a",
            fg="white",
            pady=15
        ).pack()

        tk.Label(
            wf,
            text="Test your knowledge and win up to ₹1 CRORE!",
            font=font.Font(size=14),
            bg="#0A0A2E",
            fg="white",
        ).pack(pady=10)

        start_btn = tk.Button(
            wf,
            text="🎮 START GAME 🎮",
            font=font.Font(size=16, weight="bold"),
            bg="#FF4444",
            fg="white",
            width=20,
            height=3,
            command=self.start_game,
            cursor="hand2",
            relief=tk.RAISED,
            bd=4
        )
        start_btn.pack(pady=20)
        
        # Hover effects
        def on_enter(e):
            start_btn.config(bg="#FF6666", relief=tk.SUNKEN)
        def on_leave(e):
            start_btn.config(bg="#FF4444", relief=tk.RAISED)
        
        start_btn.bind("<Enter>", on_enter)
        start_btn.bind("<Leave>", on_leave)

        rules_btn = tk.Button(
            wf,
            text="📖 HOW TO PLAY",
            font=font.Font(size=12),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            command=self.show_rules,
            cursor="hand2",
        )
        rules_btn.pack(pady=6)

        footer = tk.Label(
            wf,
            text="© 2025 KBC Live Edition - Experience the Thrill!",
            font=font.Font(size=10),
            bg="#0A0A2E",
            fg="gray",
        )
        footer.pack(side=tk.BOTTOM, pady=10)

    def animate_title(self, title_label):
        """Simple title animation"""
        try:
            current_bg = title_label.cget("bg")
            new_bg = "#FFA500" if current_bg == "#FFD700" else "#FFD700"
            title_label.config(bg=new_bg)
            self.root.after(1000, lambda: self.animate_title(title_label))
        except:
            pass

    def show_rules(self):
        rules_text = (
            "🎯 KAUN BANEGA CROREPATI - GAME RULES 🎯\n\n"
            "🎪 HOSTED BY: Amitabh Bachchan\n\n"
            "📚 HOW TO PLAY:\n"
            "• Answer 15 questions correctly to win ₹1 CRORE\n"
            "• Each question has 4 multiple choice options (A, B, C, D)\n"
            "• Click an option to select it (turns YELLOW)\n"
            "• Press ENTER or 'Lock Answer' to confirm your choice\n"
            "• You have 30 seconds per question\n"
            "• Safe havens at questions 5, 10, and 15\n\n"
            "🆘 LIFELINES (one use each):\n"
            "  - 50:50 (press 1) removes 2 wrong answers\n"
            "  - Ask the Audience (press 2) shows poll results\n"
            "  - Phone a Friend (press 3) shows friend's suggestion\n\n"
            "⚠️ RULES:\n"
            "• Wrong answer ends the game; you keep safe haven money\n"
            "• Use keyboard: A/B/C/D to select, ENTER to lock\n"
            "• F11 to toggle fullscreen, ESC to exit fullscreen\n\n"
            "🎊 Good luck and may the odds be in your favor!"
        )
        messagebox.showinfo("How to Play KBC", rules_text)

    # ---------------------
    # Game start / flow
    # ---------------------
    def start_game(self):
        self.current_question = 0
        self.score = 0
        self.lifelines_used = {"50_50": False, "audience": False, "phone": False}
        self.selected_option = None
        self.answer_locked = False
        self.awaiting_confirmation = False
        random.shuffle(self.questions)
        self.setup_game_screen()
        self.show_host_message('welcome')
        self.root.after(3000, self.load_question)

    def setup_game_screen(self):
        self.clear_screen()

        # Host area at the top
        host_frame = tk.Frame(self.main_frame, bg="#1a1a4a", relief=tk.RAISED, bd=3)
        host_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.host_label = tk.Label(
            host_frame,
            text="🎤 Amitabh Bachchan: Namaste! Chaliye shuru karte hain...",
            font=self.host_font,
            bg="#1a1a4a",
            fg="#FFD700",
            wraplength=1000,
            pady=10
        )
        self.host_label.pack()

        # Top frame: question counter and timer
        top_frame = tk.Frame(self.main_frame, bg="#0A0A2E")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        info_frame = tk.Frame(top_frame, bg="#2D2D5A", relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, pady=5)

        self.question_counter = tk.Label(
            info_frame,
            text="Question 1 of 15",
            font=font.Font(size=16, weight="bold"),
            bg="#2D2D5A",
            fg="#FFD700",
            pady=5
        )
        self.question_counter.pack(side=tk.LEFT, padx=20)

        self.timer_label = tk.Label(
            info_frame,
            text=f"⏰ Time: {self.time_limit}s",
            font=font.Font(size=16, weight="bold"),
            bg="#2D2D5A",
            fg="#FF4444",
            pady=5
        )
        self.timer_label.pack(side=tk.RIGHT, padx=20)

        self.category_label = tk.Label(
            info_frame,
            text="",
            font=font.Font(size=14, slant="italic"),
            bg="#2D2D5A",
            fg="#ADD8E6",
            pady=5
        )
        self.category_label.pack()

        # Question area
        qframe = tk.Frame(self.main_frame, bg="#1E1E5F", relief=tk.RAISED, bd=4)
        qframe.pack(fill=tk.X, padx=20, pady=15)
        
        prize_label = tk.Label(
            qframe,
            text="",
            font=font.Font(size=14, weight="bold"),
            bg="#1E1E5F",
            fg="#FFD700",
            pady=5
        )
        prize_label.pack()
        self.prize_label = prize_label
        
        self.question_label = tk.Label(
            qframe,
            text="",
            font=self.question_font,
            bg="#1E1E5F",
            fg="white",
            wraplength=1000,
            justify=tk.CENTER,
            padx=20,
            pady=25,
        )
        self.question_label.pack(fill=tk.BOTH)

        # Options (2x2 grid) with professional styling
        options_frame = tk.Frame(self.main_frame, bg="#0A0A2E")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)
        self.option_buttons = []
        option_letters = ["A", "B", "C", "D"]

        for i in range(4):
            r = i // 2
            c = i % 2
            cell = tk.Frame(options_frame, bg="#0A0A2E")
            cell.grid(row=r, column=c, padx=15, pady=12, sticky="nsew")
            options_frame.grid_rowconfigure(r, weight=1)
            options_frame.grid_columnconfigure(c, weight=1)

            # Professional option button styling
            btn = tk.Button(
                cell,
                text=f"{option_letters[i]}: ",
                font=self.option_font,
                bg="#2C2C54",  # Neutral dark blue
                fg="white",
                width=35,
                height=4,
                relief=tk.RAISED,
                bd=3,
                cursor="hand2",
                command=lambda x=i: self.select_option(x),
                activebackground="#3A3A6A",
                activeforeground="white"
            )
            btn.pack(fill=tk.BOTH, expand=True)
            
            # Professional hover effects
            def make_hover_handlers(button, index):
                def on_enter(e):
                    if button["state"] != tk.DISABLED and self.selected_option != index:
                        button.config(bg="#3A3A6A", relief=tk.SUNKEN)
                def on_leave(e):
                    if button["state"] != tk.DISABLED and self.selected_option != index:
                        button.config(bg="#2C2C54", relief=tk.RAISED)
                return on_enter, on_leave
            
            enter_handler, leave_handler = make_hover_handlers(btn, i)
            btn.bind("<Enter>", enter_handler)
            btn.bind("<Leave>", leave_handler)
            self.option_buttons.append(btn)

        # Lock answer button
        lock_frame = tk.Frame(self.main_frame, bg="#0A0A2E")
        lock_frame.pack(pady=10)
        
        self.lock_button = tk.Button(
            lock_frame,
            text="🔒 LOCK ANSWER (Press Enter)",
            font=font.Font(size=14, weight="bold"),
            bg="#FFD700",
            fg="#0A0A2E",
            width=25,
            height=2,
            command=self.lock_answer,
            cursor="hand2",
            state=tk.DISABLED,
            relief=tk.RAISED,
            bd=3
        )
        self.lock_button.pack()

        # Bottom: lifelines, money ladder, controls
        bottom = tk.Frame(self.main_frame, bg="#0A0A2E")
        bottom.pack(fill=tk.X, padx=20, pady=15)

        # Lifelines with better styling
        lf = tk.Frame(bottom, bg="#1a1a4a", relief=tk.RAISED, bd=2)
        lf.pack(side=tk.LEFT, anchor="w", padx=10)
        
        tk.Label(
            lf,
            text="🆘 LIFELINES:",
            font=font.Font(size=12, weight="bold"),
            bg="#1a1a4a",
            fg="white",
            pady=5
        ).pack(anchor="w", padx=10)

        lifebtns = tk.Frame(lf, bg="#1a1a4a")
        lifebtns.pack(anchor="w", padx=10, pady=5)

        self.lifeline_5050 = tk.Button(
            lifebtns,
            text="50:50 (1)",
            command=self.use_5050,
            font=font.Font(size=10, weight="bold"),
            bg="#9C27B0",
            fg="white",
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        )
        self.lifeline_5050.pack(side=tk.LEFT, padx=3)

        self.lifeline_audience = tk.Button(
            lifebtns,
            text="👥 Audience (2)",
            command=self.use_audience_poll,
            font=font.Font(size=10, weight="bold"),
            bg="#9C27B0",
            fg="white",
            width=14,
            height=2,
            relief=tk.RAISED,
            bd=2
        )
        self.lifeline_audience.pack(side=tk.LEFT, padx=3)

        self.lifeline_phone = tk.Button(
            lifebtns,
            text="📞 Phone (3)",
            command=self.use_phone_friend,
            font=font.Font(size=10, weight="bold"),
            bg="#9C27B0",
            fg="white",
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=2
        )
        self.lifeline_phone.pack(side=tk.LEFT, padx=3)

        # Money ladder (right) with better styling
        money_frame = tk.Frame(bottom, bg="#1a1a4a", relief=tk.RAISED, bd=2)
        money_frame.pack(side=tk.RIGHT, anchor="e", padx=10)
        
        tk.Label(
            money_frame,
            text="💰 PRIZE MONEY",
            font=font.Font(size=12, weight="bold"),
            bg="#1a1a4a",
            fg="#FFD700",
            pady=5
        ).pack()
        
        self.money_listbox = tk.Listbox(
            money_frame,
            height=10,
            width=20,
            font=self.money_font,
            bg="#2C2C54",
            fg="white",
            selectbackground="#FFD700",
            selectforeground="black",
            relief=tk.SUNKEN,
            bd=2
        )
        self.money_listbox.pack(padx=5, pady=5)
        
        # populate in descending order
        for idx, m in enumerate(reversed(self.prize_money), 1):
            self.money_listbox.insert(tk.END, f"{15 - (idx - 1):2d}. {m}")

        # Controls with better styling
        ctrl_frame = tk.Frame(bottom, bg="#1a1a4a", relief=tk.RAISED, bd=2)
        ctrl_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            ctrl_frame,
            text="⚙️ CONTROLS",
            font=font.Font(size=10, weight="bold"),
            bg="#1a1a4a",
            fg="white",
            pady=5
        ).pack()
        
        self.quit_btn = tk.Button(
            ctrl_frame,
            text="💰 QUIT & TAKE MONEY",
            command=self.quit_game,
            font=font.Font(size=9, weight="bold"),
            bg="#F44336",
            fg="white",
            width=18,
            height=2,
            relief=tk.RAISED,
            bd=2
        )
        self.quit_btn.pack(padx=5, pady=3)

        self.restart_btn = tk.Button(
            ctrl_frame,
            text="🔄 RESTART",
            command=lambda: self.start_game(),
            font=font.Font(size=9, weight="bold"),
            bg="#4CAF50",
            fg="white",
            width=18,
            height=2,
            relief=tk.RAISED,
            bd=2
        )
        self.restart_btn.pack(padx=5, pady=3)

    # ---------------------
    # Timer (uses after)
    # ---------------------
    def start_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.time_left = self.time_limit
        self.timer_running = True
        self.update_timer_display()
        self._countdown_tick()

    def _countdown_tick(self):
        if not self.timer_running:
            return
        self.timer_label.config(text=f"⏰ Time: {self.time_left}s")
        if self.time_left <= 10:
            self.timer_label.config(fg="#FF0000")
        else:
            self.timer_label.config(fg="#FF4444")
        if self.time_left <= 0:
            self.timer_running = False
            self.time_up()
            return
        self.time_left -= 1
        self.timer_id = self.root.after(1000, self._countdown_tick)

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_running = False

    def update_timer_display(self):
        self.timer_label.config(text=f"⏰ Time: {self.time_left}s")

    def time_up(self):
        self.show_host_message('wrong')
        messagebox.showwarning("Time Up!", "🕐 Time's up! Game Over.")
        self.end_game(False)

    # ---------------------
    # Loading question & UI updates
    # ---------------------
    def load_question(self):
        if self.current_question >= len(self.questions):
            self.end_game(True)
            return

        qdata = self.questions[self.current_question]
        self.question_counter.config(text=f"Question {self.current_question + 1} of {len(self.questions)}")
        self.category_label.config(text=f"📚 Category: {qdata.get('category','')}")
        self.prize_label.config(text=f"🏆 Playing for: {self.prize_money[self.current_question]}")
        self.question_label.config(text=qdata["question"])
        letters = ["A", "B", "C", "D"]

        # reset option buttons to neutral state
        for i, btn in enumerate(self.option_buttons):
            btn.config(
                text=f"{letters[i]}: {qdata['options'][i]}",
                state=tk.NORMAL,
                bg="#2C2C54",  # Neutral color
                fg="white",
                relief=tk.RAISED,
            )

        # highlight current money level in listbox
        self.money_listbox.selection_clear(0, tk.END)
        select_index = 14 - self.current_question
        if 0 <= select_index <= 14:
            self.money_listbox.selection_set(select_index)

        # enable/disable lifeline buttons
        self.lifeline_5050.config(state=tk.NORMAL if not self.lifelines_used["50_50"] else tk.DISABLED)
        self.lifeline_audience.config(state=tk.NORMAL if not self.lifelines_used["audience"] else tk.DISABLED)
        self.lifeline_phone.config(state=tk.NORMAL if not self.lifelines_used["phone"] else tk.DISABLED)

        # Reset selection state
        self.selected_option = None
        self.answer_locked = False
        self.awaiting_confirmation = False
        self.lock_button.config(state=tk.DISABLED)
        
        # Show host introduction for question
        self.show_host_message('question_intro')
        
        # start timer after brief delay
        self.root.after(1500, self.start_timer)

    # ---------------------
    # Answer selection with lock mechanism
    # ---------------------
    def select_option(self, option_index):
        # ignore if not running or if awaiting confirmation
        if not self.timer_running or self.awaiting_confirmation:
            return
        # Also ignore if button disabled
        if self.option_buttons[option_index]["state"] == tk.DISABLED:
            return

        # Clear previous selection
        if self.selected_option is not None:
            self.option_buttons[self.selected_option].config(
                bg="#2C2C54", 
                fg="white",
                relief=tk.RAISED
            )

        # Set new selection with YELLOW highlight
        self.selected_option = option_index
        self.option_buttons[option_index].config(
            bg="#FFD700",  # Yellow for selection
            fg="black",
            relief=tk.SUNKEN
        )
        
        # Enable lock button
        self.lock_button.config(state=tk.NORMAL, bg="#FF4444")
        
        # Update host message
        option_letter = chr(65 + option_index)
        self.host_label.config(text=f"🎤 Amitabh Bachchan: Aap {option_letter} select kar rahe hain... Final answer?")

    def lock_answer(self):
        """Lock the selected answer and reveal result"""
        if self.selected_option is None or self.awaiting_confirmation or not self.timer_running:
            return
            
        # Confirm lock
        result = messagebox.askyesno(
            "Lock Answer", 
            f"Are you sure you want to lock Option {chr(65 + self.selected_option)}?\n"
            f"This will be your final answer!"
        )
        
        if not result:
            return
            
        self.awaiting_confirmation = True
        self.stop_timer()
        self.lock_button.config(state=tk.DISABLED, bg="gray")
        
        # Host dramatic pause
        self.host_label.config(text="🎤 Amitabh Bachchan: Computer ji, lock kiya jaye?")
        
        # Process the locked answer after dramatic pause
        self.root.after(2000, self._reveal_answer)

    def key_select(self, idx):
        """Handle keyboard selection"""
        try:
            if 0 <= idx < len(self.option_buttons):
                self.select_option(idx)
        except Exception:
            pass

    def _reveal_answer(self):
        """Reveal the correct answer with colors"""
        qdata = self.questions[self.current_question]
        correct_idx = qdata["correct"]
        chosen_idx = self.selected_option
        
        # Color coding: Green for correct, Red for wrong choice
        for i, btn in enumerate(self.option_buttons):
            if i == correct_idx:
                btn.config(bg="#4CAF50", fg="white")  # Green for correct
            elif i == chosen_idx and i != correct_idx:
                btn.config(bg="#F44336", fg="white")  # Red for wrong choice
            # Other options remain neutral

        # Process result after brief display
        self.root.after(1500, lambda: self._process_choice(chosen_idx == correct_idx))

    def _process_choice(self, was_correct):
        if was_correct:
            self.score = self.current_question + 1
            self.show_host_message('correct')
            # Optional sound on correct
            if SOUND_AVAILABLE:
                try:
                    # You can replace with a valid sound file path
                    pass
                except Exception:
                    pass
            
            # Special message for milestones
            current_amount = self.prize_money[self.current_question]
            if self.current_question in self.safe_havens:
                messagebox.showinfo(
                    "🎉 Correct! Safe Haven Reached!",
                    f"Excellent! You've won {current_amount}!\n🏆 This is a SAFE HAVEN - you're guaranteed this amount!"
                )
            else:
                messagebox.showinfo(
                    "🎉 Correct!",
                    f"Shabash! You've won {current_amount}!"
                )
            
            self.current_question += 1
            if self.current_question >= len(self.questions):
                self.end_game(True)
            else:
                self.root.after(1000, self.load_question)
        else:
            # wrong answer flow
            self.show_host_message('wrong')
            self.wrong_answer()

    # ---------------------
    # Wrong / Quit / End game
    # ---------------------
    def wrong_answer(self):
        # find safe money
        safe_money = None
        for s in reversed(self.safe_havens):
            if self.current_question > s:
                safe_money = self.prize_money[s]
                break

        if safe_money:
            messagebox.showinfo(
                "❌ Wrong Answer", 
                f"Wrong answer! But you've reached a safe haven.\n💰 You're taking home {safe_money}!"
            )
        else:
            messagebox.showinfo(
                "❌ Wrong Answer", 
                "Wrong answer! Game Over.\n💔 You're going home empty-handed."
            )
        self.end_game(False)

    def quit_game(self):
        # Determine current money if quitting
        if self.current_question == 0:
            money = "₹0"
        else:
            # Last completed question index = current_question - 1
            last_completed = self.current_question - 1
            # check safe haven passed
            money = None
            for s in reversed(self.safe_havens):
                if last_completed >= s:
                    money = self.prize_money[s]
                    break
            if money is None and last_completed >= 0:
                money = self.prize_money[last_completed]
            elif money is None:
                money = "₹0"
                
        result = messagebox.askyesno(
            "Quit Game", 
            f"🤔 Amitabh Bachchan: 'Kya aap confirm hain?'\n\n💰 You'll take home: {money}\n\nAre you sure?"
        )
        if result:
            self.host_label.config(text="🎤 Amitabh Bachchan: Dhanyawad! Aap bahut achha khele!")
            messagebox.showinfo("Game Over", f"🙏 Thanks for playing!\n💰 You're taking home: {money}")
            self.show_welcome_screen()

    def end_game(self, won):
        self.stop_timer()
        if won:
            self.host_label.config(text="🎤 Amitabh Bachchan: KOTI KOTI BADHAI! Aap jeet gaye 1 CRORE!")
            messagebox.showinfo(
                "🏆 JACKPOT! 🏆", 
                "🎉🎉 INCREDIBLE! 🎉🎉\n\n💰 You've won ₹1 CRORE! 💰\n\n🏆 You're the ultimate KBC champion! 🏆\n\n"
                "🎊 Amitabh Bachchan: 'Aap kamaal kar diye!' 🎊"
            )
        else:
            # Determine safe money
            safe_money = None
            for s in reversed(self.safe_havens):
                if self.current_question > s:
                    safe_money = self.prize_money[s]
                    break
            if safe_money:
                messagebox.showinfo("Game Over", f"🎭 Game Over!\n💰 You're taking home: {safe_money}")
            else:
                messagebox.showinfo("Game Over", "🎭 Game Over!\n💔 Better luck next time!")

        play_again = messagebox.askyesno("Play Again?", "🎮 Would you like to play another game?")
        if play_again:
            self.start_game()
        else:
            self.show_welcome_screen()

    # ---------------------
    # Lifelines with host integration
    # ---------------------
    def use_5050(self):
        if self.lifelines_used["50_50"] or not self.timer_running:
            return
        
        self.show_host_message('lifeline')
        self.lifelines_used["50_50"] = True
        self.lifeline_5050.config(state=tk.DISABLED, bg="gray")
        
        correct = self.questions[self.current_question]["correct"]
        wrongs = [i for i in range(4) if i != correct and self.option_buttons[i]["state"] == tk.NORMAL]
        
        if len(wrongs) <= 1:
            return
            
        to_remove = random.sample(wrongs, 2)
        for i in to_remove:
            self.option_buttons[i].config(state=tk.DISABLED, bg="gray", fg="darkgray")
            
        messagebox.showinfo(
            "🔥 50:50 Lifeline", 
            "🎯 Two wrong answers have been removed!\n\n🎤 Amitabh Bachchan: 'Ab sirf do options bach gaye hain!'"
        )

    def use_audience_poll(self):
        if self.lifelines_used["audience"] or not self.timer_running:
            return
            
        self.show_host_message('lifeline')
        self.lifelines_used["audience"] = True
        self.lifeline_audience.config(state=tk.DISABLED, bg="gray")
        
        correct = self.questions[self.current_question]["correct"]

        # Build realistic poll ensuring sum 100 and correct gets majority
        poll = [0, 0, 0, 0]
        poll[correct] = random.randint(45, 75)
        remaining = 100 - poll[correct]
        others = [i for i in range(4) if i != correct]
        
        # distribute remaining among others
        for i in range(len(others) - 1):
            alloc = random.randint(0, remaining)
            poll[others[i]] = alloc
            remaining -= alloc
        poll[others[-1]] = remaining

        poll_text = "👥 AUDIENCE POLL RESULTS 👥\n\n"
        poll_text += "🎤 Amitabh Bachchan: 'Audience ke paas jawab hai!'\n\n"
        for i, p in enumerate(poll):
            option_letter = chr(65 + i)
            poll_text += f"Option {option_letter}: {p}% {'📊' * (p//10)}\n"
        
        poll_text += f"\n🎯 Highest vote: Option {chr(65 + poll.index(max(poll)))} ({max(poll)}%)"
        messagebox.showinfo("Ask the Audience", poll_text)

    def use_phone_friend(self):
        if self.lifelines_used["phone"] or not self.timer_running:
            return
            
        self.show_host_message('lifeline')
        self.lifelines_used["phone"] = True
        self.lifeline_phone.config(state=tk.DISABLED, bg="gray")
        
        correct = self.questions[self.current_question]["correct"]
        friends = [
            ("Rajesh Kumar", "Software Engineer"), 
            ("Dr. Priya Sharma", "Doctor"), 
            ("Prof. Amit Singh", "Teacher"), 
            ("Adv. Sunita Gupta", "Lawyer")
        ]
        friend_name, friend_profession = random.choice(friends)
        
        # Friend is usually right (85% chance)
        if random.random() < 0.85:
            suggestion = chr(65 + correct)
            confidence_phrases = [
                "quite confident", "pretty sure", "fairly certain", 
                "strongly believe", "almost certain"
            ]
            confidence = random.choice(confidence_phrases)
        else:
            others = [i for i in range(4) if i != correct]
            suggestion = chr(65 + random.choice(others))
            confidence = "not very sure, but I think"

        message = f"📞 PHONE A FRIEND 📞\n\n"
        message += f"🎤 Amitabh Bachchan: 'Chaliye phone milate hain...'\n\n"
        message += f"👤 {friend_name} ({friend_profession}):\n"
        message += f"'Hello! I'm {confidence} the answer is Option {suggestion}.'\n\n"
        message += f"🎤 'Thank you {friend_name.split()[0]}!'"
        
        messagebox.showinfo("Phone a Friend", message)

    # ---------------------
    # Run
    # ---------------------
    def run(self):
        # center window on start
        self.root.update_idletasks()
        w = 1400
        h = 900
        try:
            x = (self.root.winfo_screenwidth() // 2) - (w // 2)
            y = (self.root.winfo_screenheight() // 2) - (h // 2)
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass
        self.root.mainloop()


if __name__ == "__main__":
    print("🎬 Starting Kaun Banega Crorepati - Live Edition with Amitabh Bachchan...")
    print("🎯 Features: Professional UI, Host Commentary, Lock Answer System!")
    game = KBCGame()
    game.run()