import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import subprocess
import re
import psutil
import shutil
import time
import threading
import math
# ΑΠΑΡΑΙΤΗΤΟ ΓΙΑ PNG ΕΙΚΟΝΙΔΙΑ ΣΗΜΑΙΩΝ: pip install Pillow
try:
    from PIL import Image, ImageTk 
    import io
    import base64
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    
# *** ΣΗΜΑΝΤΙΚΟ: ΧΡΕΙΑΖΕΤΑΙ Η PIL (Pillow) ΓΙΑ ΝΑ ΔΟΥΛΕΨΟΥΝ ΟΙ ΣΗΜΑΙΕΣ! ***

class DCSMapMoverApp:
    # Καθορισμός της έκδοσης
    VERSION = "2.4.8" # Νέα έκδοση με επαναφορά του DCS Running σε messagebox
    TITLE_GR = f"MM DCS v.{VERSION}® 2025© for LOCK-ON GREECE by =GR= Astr0"
    TITLE_EN = f"MM DCS v.{VERSION}® 2025© for LOCK-ON GREECE by =GR= Astr0"

    DCS_PROCESS_NAMES = ["DCS.exe", "DCS_updater.exe"] # Λίστα διεργασιών για έλεγχο
    
    # --- Μεταφράσεις (Translations) ---
    TRANSLATIONS = {
        'gr': {
            'title': TITLE_GR,
            'path_label': "1. Φάκελος Εγκατάστασης DCS World:",
            'path_default': "Δεν έχει επιλεγεί",
            'path_button': "Επιλογή Φακέλου",
            'mode_move': "2. Μεταφορά Χαρτών",
            'mode_restore': "3. Επαναφορά Χαρτών",
            'dest_label': "Φάκελος Προορισμού:",
            'dest_default_move': "Δεν έχει οριστεί προορισμός μετακίνησης. . .",
            'dest_default_restore': "Μη Διαθέσιμο σε Επαναφορά",
            'dest_button': "Επιλογή Φακέλου",
            'restore_button': "Επιλογή Χαρτών",
            'execute_button': "Εκτέλεση Τώρα",
            'close_button': "Κλείσιμο", 
            'progress_default': "Αναμονή επιλογής φακέλου DCS...",
            'progress_select_mode': "Επιλέξτε 'Μεταφορά' ή 'Επαναφορά'",
            'progress_select_maps_move': "Επιλέξτε τους χάρτες προς μεταφορά.",
            'progress_select_dest': "Παρακαλώ πατήστε 'Επιλογή Φακέλου' και επιλέξτε προορισμό.",
            'progress_ready_move': "Έτοιμο για Μετακίνηση! Προορισμός: ",
            'progress_ready_restore': "Έτοιμο για Επαναφορά!",
            'maps_title_move': "Επιλογή Xαρτών προς Μεταφορά",
            'maps_title_restore': "Επιλογή Χαρτών προς Επαναφορά",
            'maps_size_label': "Συνολικό Μέγεθος: ",
            'maps_not_found': "Δεν βρέθηκαν κατάλληλοι χάρτες.",
            'maps_restored': "Μετακινημένος: ",
            'error_path_title': "Σφάλμα",
            'error_path_msg': "Ο φάκελος που επιλέξατε δεν φαίνεται να είναι ο σωστός φάκελος του DCS World. Δεν βρέθηκε ο φάκελος 'Mods\\terrains'.",
            'warning_dest_title': "Προσοχή",
            'warning_dest_msg': "Ο φάκελος προορισμού δεν μπορεί να βρίσκεται μέσα στον φάκελο εγκατάστασης του DCS World.",
            'error_space_title': "Σφάλμα Χώρου",
            'error_space_msg': "Ο επιλεγμένος δίσκος δεν έχει επαρκή ελεύθερο χώρο.\n\nΑπαιτούνται: ",
            'error_space_available': "\nΔιαθέσιμα: ",
            'warning_admin_title': "Προσοχή",
            'warning_admin_msg': "Για τη δημιουργία συνδέσμων (Junctions) απαιτούνται δικαιώματα διαχειριστή. Η εκτέλεση μπορεί να αποτύχει.",
            
            # Μήνυμα Σφάλματος Admin (Custom Toplevel - διατηρείται για γραμματοσειρά 12)
            'error_admin_startup_msg': "Η εφαρμογή απαιτεί δικαιώματα διαχειριστή (Run as Administrator) για να εκτελέσει τη μεταφορά χαρτών. \n\nΠαρακαλώ κλείστε και επανεκκινήστε την εφαρμογή \nκάνοντας δεξί κλικ στο εκτελέσιμο αρχείο (.exe) και επιλέγοντας \n'Εκτέλεση ως διαχειριστής'.\n\n---\n\n[EN]\n\nAdministrator Rights Required\n\nThis application requires administrator rights (Run as Administrator) to perform map movement operations (creating Junctions).\n\nPlease close and restart the application \nby right-clicking the executable file (.exe) and selecting \n'Run as administrator'.", 
            
            # Μήνυμα Σφάλματος DCS Running (Για χρήση σε messagebox.showerror)
            'error_dcs_running_msg': "[GR]\n\nΚλείσε το DCS World για να τρέξει το πρόγραμμα!\n\nΑυτό το εργαλείο δεν μπορεί να λειτουργήσει όσο τρέχει το παιχνίδι (DCS.exe ή DCS_updater.exe).\n\nΠαρακαλώ κλείστε και επανεκκινήστε την εφαρμογή, αφού πρώτα βεβαιωθείτε ότι το DCS World δεν εκτελείται.\n\n---\n\n[EN]\n\nClose DCS World to run the program!\n\nThis tool cannot operate while the game is running (DCS.exe or DCS_updater.exe).\n\nPlease close and restart the application, after ensuring DCS World is not running.",
            
            'exec_moving': "Εκτέλεση Μετακίνησης...",
            'exec_restoring': "Εκτέλεση Επαναφοράς...",
            'exec_fail_title': "Σφάλμα Λειτουργίας",
            'exec_fail_msg': "Η διαδικασία απέτυχε ή ακυρώθηκε.",
            'exec_success_title_move': "Επιτυχής Ολοκλήρωση Μετακίνησης",
            'exec_success_title_restore': "Επιτυχής Ολοκλήρωση Επαναφοράς",
            'exec_success_msg': "Η διαδικασία ολοκληρώθηκε επιτυχώς!",
            'exec_warning_title_move': "Ολοκλήρωση Μετακίνηση με Σφάλματα",
            'exec_warning_title_restore': "Ολοκλήρωση Επαναφοράς με Σφάλματα",
            'exec_warning_msg_prefix': "Η διαδικασία ολοκληρώθηκε. Πιθανά σφάλματα:\n\n",
            'exec_disk_error': "Σφάλμα Δημιουργίας/Πρόσβασης στον προορισμό: ",
            'progress_done': "Ολοκληρώθηκε. Επιλέξτε 'Μεταφορά' ή 'Επαναφορά'."
        },
        'en': {
            'title': TITLE_EN,
            'path_label': "1. DCS World Installation Folder:",
            'path_default': "Not selected",
            'path_button': "Select Folder",
            'mode_move': "2. Move Maps",
            'mode_restore': "3. Restore Maps",
            'dest_label': "Destination Folder:",
            'dest_default_move': "No destination path defined. . .",
            'dest_default_restore': "Not Available in Restore Mode",
            'dest_button': "Select Folder",
            'restore_button': "Select Maps",
            'execute_button': "Execute Now",
            'close_button': "Close", 
            'progress_default': "Waiting for DCS folder selection...",
            'progress_select_mode': "Select 'Move' or 'Restore'",
            'progress_select_maps_move': "Select the maps to move.",
            'progress_select_dest': "Please click 'Select Folder' and choose a destination.",
            'progress_ready_move': "Ready to Move! Destination: ",
            'progress_ready_restore': "Ready to Restore!",
            'maps_title_move': "Select Maps to Move",
            'maps_title_restore': "Select Maps to Restore",
            'maps_size_label': "Total Size: ",
            'maps_not_found': "No suitable maps found.",
            'maps_restored': "Moved to: ",
            'error_path_title': "Error",
            'error_path_msg': "The selected folder does not appear to be the correct DCS World folder. 'Mods\\terrains' not found.",
            'warning_dest_title': "Attention",
            'warning_dest_msg': "The destination folder cannot be inside the DCS World installation folder.",
            'error_space_title': "Space Error",
            'error_space_msg': "The selected disk does not have enough free space.\n\nRequired: ",
            'error_space_available': "\nAvailable: ",
            'warning_admin_title': "Attention",
            'warning_admin_msg': "Administrator rights are required to create symbolic links (Junctions). Execution may fail.",
            
            # Μήνυμα Σφάλματος Admin (Custom Toplevel - διατηρείται για γραμματοσειρά 12)
            'error_admin_startup_msg': "The application requires administrator rights (Run as Administrator) to perform map movement. \n\nPlease close and restart the application \nby right-clicking the executable file (.exe) and selecting \n'Run as administrator'.\n\n---\n\n[GR]\n\nΑπαιτούνται Δικαιώματα Διαχειριστή\n\nΗ εφαρμογή απαιτεί δικαιώματα διαχειριστή (Run as Administrator) για να εκτελέσει τη μεταφορά χαρτών (δημιουργία Junctions).\n\nΠαρακαλώ κλείστε και επανεκκινήστε την εφαρμογή \nκάνοντας δεξί κλικ στο εκτελέσιμο αρχείο (.exe) και επιλέγοντας \n'Εκτέλεση ως διαχειριστής'.",
            
            # Μήνυμα Σφάλματος DCS Running (Για χρήση σε messagebox.showerror)
            'error_dcs_running_msg': "Close DCS World to run the program!\n\nThis tool cannot operate while the game is running (DCS.exe or DCS_updater.exe).\n\nPlease close and restart the application, after ensuring DCS World is not running.\n\n---\n\n[GR]\n\nΚλείσε το DCS World για να τρέξει το πρόγραμμα!\n\nΑυτό το εργαλείο δεν μπορεί να λειτουργήσει όσο τρέχει το παιχνίδι (DCS.exe ή DCS_updater.exe).\n\nΠαρακαλώ κλείστε και επανεκκινήστε την εφαρμογή, αφού πρώτα βεβαιωθείτε ότι το DCS World δεν εκτελείται.", 
            
            'exec_moving': "Executing Move...",
            'exec_restoring': "Executing Restore...",
            'exec_fail_title': "Operation Error",
            'exec_fail_msg': "The process failed or was cancelled.",
            'exec_success_title_move': "Move Completed Successfully",
            'exec_success_title_restore': "Restore Completed Successfully",
            'exec_success_msg': "The process completed successfully!",
            'exec_warning_title_move': "Move Completed with Errors",
            'exec_warning_title_restore': "Restore Completed with Errors",
            'exec_warning_msg_prefix': "The process completed. Potential errors:\n\n",
            'exec_disk_error': "Error Creating/Accessing destination: ",
            'progress_done': "Completed. Select 'Move' or 'Restore'."
        }
    }
    
    # --- Εικόνες Base64 (Flags Base64) ---
    FLAG_GR_BASE64 = b'' 
    FLAG_EN_BASE64 = b''

    def __init__(self, master):
        self.master = master
        
        self.current_lang = 'gr' 
        self.lang_var = tk.StringVar(value=self.current_lang) 

        # Βασικές Μεταβλητές
        self.dcs_path = None
        self.terrains_path = None
        self.maps = {} 
        self.linked_maps = {} 
        self.map_vars = {} 
        self.restore_map_vars = {}
        self.target_path = tk.StringVar(value="")
        self.selected_maps_size = 0
        self.current_mode = None 
        
        # GUI Setup
        if PILLOW_AVAILABLE:
            self.load_images()
        else:
            self.flag_gr_img = None
            self.flag_en_img = None

        self.create_widgets()
        self.set_initial_state()
        self.update_texts() 
        
        # *** ΕΛΕΓΧΟΣ DCS RUNNING ΣΤΗΝ ΕΚΚΙΝΗΣΗ ***
        if os.name == 'nt' and self.is_dcs_running():
            self.show_dcs_running_warning() # Χρησιμοποιεί messagebox
        
        # *** ΕΛΕΓΧΟΣ ADMIN ΣΤΗΝ ΕΚΚΙΝΗΣΗ ***
        elif os.name == 'nt' and not self.is_admin():
            self.show_startup_admin_warning() # Χρησιμοποιεί custom Toplevel


    def is_dcs_running(self):
        """Ελέγχει αν το DCS World (DCS.exe, DCS_updater.exe) τρέχει (μόνο για Windows)."""
        if os.name == 'nt':
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in self.DCS_PROCESS_NAMES:
                    return True
        return False


    # ΝΕΑ ΣΥΝΑΡΤΗΣΗ: Επαναφορά σε messagebox.showerror για την οπτική εμφάνιση της εικόνας
    def show_dcs_running_warning(self):
        """Εμφανίζει προειδοποίηση ότι το DCS τρέχει και κλείνει την εφαρμογή (με messagebox)."""
        
        self.master.withdraw() 
        
        title = self.get_text('exec_fail_title') 
        # Χρησιμοποιούμε το μήνυμα από τα Ελληνικά, το οποίο τώρα έχει την μορφοποίηση (GR, EN) για messagebox
        message = self.TRANSLATIONS['gr'].get('error_dcs_running_msg')
        
        # Εμφάνιση του τυπικού MessageBox
        messagebox.showerror(title, message)
        
        # Κλείσιμο εφαρμογής μετά το κλείσιμο του messagebox
        self.master.destroy()


    def show_startup_admin_warning(self):
        """Εμφανίζει ένα προειδοποιητικό μήνυμα κατά την εκκίνηση και κλείνει την εφαρμογή (Custom Toplevel)."""
        
        # Κρύβουμε το κύριο παράθυρο μέχρι να αποφασίσει ο χρήστης
        self.master.withdraw() 
        
        title = self.get_text('exec_fail_title') 
        # Χρησιμοποιούμε το μήνυμα από τα Ελληνικά (που περιέχει και τα Αγγλικά)
        message = self.TRANSLATIONS['gr'].get('error_admin_startup_msg')
        
        dialog = tk.Toplevel(self.master)
        dialog.title(title)
        dialog.geometry("800x600") 
        dialog.resizable(False, False)
        # Αν κλείσει το παράθυρο, κλείνει και το κύριο (και όλη η εφαρμογή)
        dialog.protocol("WM_DELETE_WINDOW", self.master.destroy) 
        dialog.grab_set() 
        
        # Κεντράρισμα του παραθύρου
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (width // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (height // 2)
        dialog.geometry('+%d+%d' % (x, y))
        
        frame = ttk.Frame(dialog, padding="40") 
        frame.pack(fill='both', expand=True)
        
        # Μεγάλη γραμματοσειρά για τον τίτλο
        ttk.Label(frame, text=title, font=('Arial', 24, 'bold')).pack(pady=(5, 20))
        
        # Γραμματοσειρά 12 και στοίχιση αριστερά (όπως ζήτησες στην προηγούμενη απάντηση)
        message_label = ttk.Label(frame, 
                                  text=message, 
                                  font=('Arial', 12),
                                  anchor='w',       # Αγκύρωση (alignment) αριστερά
                                  justify=tk.LEFT) # Στοίχιση κειμένου αριστερά
        message_label.pack(fill='x', pady=20)
        
        # [ Κλείσιμο ] button that destroys the main window (and thus the application)
        ttk.Button(frame, text=self.get_text('close_button'), command=self.master.destroy, style='TButton', width=15).pack(pady=30)
        
        # Περιμένουμε μέχρι να κλείσει το dialog (μέσω του button ή του X)
        self.master.wait_window(dialog)
        
    def load_images(self):
        """Φορτώνει τις εικόνες σημαιών από Base64."""
        self.flag_gr_img = self._load_base64_image(self.FLAG_GR_BASE64)
        self.flag_en_img = self._load_base64_image(self.FLAG_EN_BASE64)

    def _load_base64_image(self, b64_data, size=(20, 20)):
        """Βοηθητική συνάρτηση για φόρτωση εικόνας PNG από Base64 χρησιμοποιώντας PIL."""
        if not b64_data:
            return None 
        try:
            image_data = base64.b64decode(b64_data)
            image = Image.open(io.BytesIO(image_data))
            image = image.resize(size)
            return ImageTk.PhotoImage(image)
        except Exception:
            return None 
        
    def create_widgets(self):
        # --- Frame 1: Header + Language Selection ---
        header_frame = ttk.Frame(self.master, padding="15") 
        header_frame.pack(fill='x')
        
        # Τίτλος (Αριστερά)
        self.title_label = ttk.Label(header_frame, text=self.TITLE_GR, font=('Arial', 14, 'bold'))
        self.title_label.pack(side='left', anchor='w')
        
        # Επιλογή Γλώσσας (Δεξιά)
        lang_frame = ttk.Frame(header_frame)
        lang_frame.pack(side='right', anchor='e')
        
        # Ελληνική Σημαία
        self.gr_button = ttk.Radiobutton(lang_frame, 
                                         image=self.flag_gr_img, 
                                         text="GR" if not self.flag_gr_img else "", 
                                         compound='image',
                                         value='gr', 
                                         variable=self.lang_var, 
                                         command=lambda: self.set_language('gr'))
        self.gr_button.pack(side='left', padx=5)
        
        # Αγγλική Σημαία
        self.en_button = ttk.Radiobutton(lang_frame, 
                                         image=self.flag_en_img, 
                                         text="EN" if not self.flag_en_img else "", 
                                         compound='image',
                                         value='en', 
                                         variable=self.lang_var, 
                                         command=lambda: self.set_language('en'))
        self.en_button.pack(side='left', padx=5)

        ttk.Separator(header_frame, orient='horizontal').pack(fill='x', pady=8, side='bottom')
        
        # --- Frame 2: Path Selection & Mode Buttons ---
        main_controls_frame = ttk.Frame(self.master, padding="15")
        main_controls_frame.pack(fill='x')

        # 1. DCS Path Selection (Βήμα 1)
        self.path_label = ttk.Label(main_controls_frame, text="", font=('Arial', 11))
        self.path_label.grid(row=0, column=0, sticky='w', pady=8)
        
        self.path_display_label = ttk.Label(main_controls_frame, text="", foreground='red', font=('Arial', 11))
        self.path_display_label.grid(row=0, column=1, sticky='w', padx=8)
        
        self.select_dcs_button = ttk.Button(main_controls_frame, text="", command=self.manual_select_dcs_path, style='TButton', width=18)
        self.select_dcs_button.grid(row=0, column=2, sticky='e')
        
        main_controls_frame.grid_columnconfigure(1, weight=1) 

        ttk.Separator(main_controls_frame, orient='horizontal').grid(row=1, columnspan=4, sticky='ew', pady=8)

        # 2. & 3. Mode Selection & Destination Path
        
        # 2. Μεταφορά (Αριστερά)
        self.move_mode_button = ttk.Button(main_controls_frame, text="", command=lambda: self.switch_mode('move'), style='TButton', width=20)
        self.move_mode_button.grid(row=2, column=0, sticky='w', pady=4)
        
        # 3. Προορισμός Χαρτών (Κέντρο, για Μεταφορά)
        self.dest_label = ttk.Label(main_controls_frame, text="", font=('Arial', 11))
        self.dest_label.grid(row=2, column=1, sticky='e', padx=(10, 0))
        
        self.target_path_display = ttk.Label(main_controls_frame, textvariable=self.target_path, 
                                             foreground='red', 
                                             font=('Arial', 11))
        self.target_path_display.grid(row=2, column=2, sticky='w', padx=(5, 0))
        
        # Κουμπί Επιλογής Προορισμού 
        self.select_target_button = ttk.Button(main_controls_frame, text="", command=self.browse_for_target_path, style='TButton', width=18, state=tk.DISABLED)
        self.select_target_button.grid(row=2, column=3, sticky='e', padx=(8, 0))
        
        main_controls_frame.grid_columnconfigure(2, weight=1) 

        # 4. Επαναφορά (Κάτω Αριστερά) 
        self.restore_mode_button = ttk.Button(main_controls_frame, text="", command=lambda: self.switch_mode('restore'), style='TButton', width=20)
        self.restore_mode_button.grid(row=3, column=0, sticky='w', pady=4)
        
        ttk.Separator(main_controls_frame, orient='horizontal').grid(row=4, columnspan=4, sticky='ew', pady=8)

        # --- Frame 3: Dynamic Content (Επιλογή Χαρτών) ---
        self.content_frame = ttk.Frame(self.master)
        self.content_frame.pack(fill='both', expand=True, padx=15, pady=8)
        
        self.map_selection_frame = ttk.Frame(self.content_frame) 

        # --- Frame 4: Execution Button & Progress (ΕΝΣΩΜΑΤΩΜΕΝΟ) ---
        execution_frame = ttk.Frame(self.master, padding="15")
        execution_frame.pack(fill='x')
        
        # Ενσωματωμένη Μπάρα Προόδου
        self.progress_bar = ttk.Progressbar(execution_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(fill='x', pady=8)
        
        # Ενσωματωμένη Ετικέτα Προόδου (ή Ετοιμότητας)
        self.progress_label_main = ttk.Label(execution_frame, text="", anchor='center', font=('Arial', 11))
        self.progress_label_main.pack(fill='x')
        
        self.execute_button = ttk.Button(execution_frame, text="", command=self.start_execution_thread, state=tk.DISABLED, style='Accent.TButton', width=30)
        self.execute_button.pack(pady=15)

        # Custom Style
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'), foreground='black', background='lightgreen') 
        style.map('Accent.TButton', background=[('active', 'green')])
        style.configure('TButton', font=('Arial', 11))
        style.configure('TLabel', font=('Arial', 11))
        style.configure('TCheckbutton', font=('Arial', 11))
        style.configure('TLabelframe.Label', font=('Arial', 12, 'bold'))
        
        # Εγγραφή trace για το target_path
        self.target_path.trace_add('write', self.check_execution_readiness)
        
    def set_language(self, lang):
        """Θέτει την τρέχουσα γλώσσα και ενημερώνει όλα τα κείμενα."""
        self.current_lang = lang
        self.lang_var.set(lang)
        self.update_texts()
        
    def get_text(self, key):
        """Επιστρέφει το κείμενο για την τρέχουσα γλώσσα."""
        return self.TRANSLATIONS[self.current_lang].get(key, key)
        
    def update_texts(self):
        """Ενημερώνει όλα τα κείμενα στο GUI."""
        lang = self.current_lang
        
        # Header
        self.master.title(self.get_text('title'))
        self.title_label.config(text=self.get_text('title'))
        
        # Controls Frame
        self.path_label.config(text=self.get_text('path_label'))
        self.select_dcs_button.config(text=self.get_text('path_button'))
        
        self.move_mode_button.config(text=self.get_text('mode_move'))
        self.restore_mode_button.config(text=self.get_text('mode_restore'))
        
        self.dest_label.config(text=self.get_text('dest_label'))
        self.select_target_button.config(text=self.get_text('dest_button'))
        
        self.execute_button.config(text=self.get_text('execute_button'))
        
        # Ενημέρωση ετικετών κατάστασης 
        self.path_display_label.config(text=self.get_text('path_default') if not self.dcs_path else self.dcs_path)
        self.update_destination_display()
        
        if self.current_mode == 'move' or self.current_mode == 'restore':
            self.check_execution_readiness() 
        else:
             self.progress_label_main.config(text=self.get_text('progress_default'))

        # Επανεμφάνιση χαρτών (για ενημέρωση τίτλου και κειμένων)
        if self.map_selection_frame.winfo_ismapped():
            self.show_map_selection_view() 


    # --- Λογική Προγράμματος ---

    def set_initial_state(self):
        """Αρχική απενεργοποίηση κουμπιών Μετακίνησης/Επαναφοράς."""
        self.move_mode_button.config(state=tk.DISABLED)
        self.restore_mode_button.config(state=tk.DISABLED)
        self.select_target_button.config(state=tk.DISABLED) 
        self.execute_button.config(state=tk.DISABLED)
        self.progress_bar.config(value=0, mode='determinate')
        self.progress_label_main.config(text=self.get_text('progress_default'))
        
        self.map_selection_frame.pack_forget()

    def update_path_labels(self):
        """Ενημερώνει τις ετικέτες και ενεργοποιεί τα κουμπιά mode."""
        if self.dcs_path:
            self.path_display_label.config(text=self.dcs_path, foreground='darkgreen')
            
            self.move_mode_button.config(state=tk.NORMAL)
            self.restore_mode_button.config(state=tk.NORMAL)
            self.progress_label_main.config(text=self.get_text('progress_select_mode'))
            
            self.load_maps()
        else:
            self.path_display_label.config(text=self.get_text('path_default'), foreground='red')
            self.set_initial_state()

    def manual_select_dcs_path(self):
        """Επιτρέπει χειροκίνητη επιλογή του φακέλου του DCS World."""
        folder = filedialog.askdirectory(title=self.get_text('path_label'))
        if folder:
            temp_terrains_path = os.path.join(folder, 'Mods', 'terrains')
            if os.path.exists(temp_terrains_path):
                self.dcs_path = folder
                self.terrains_path = temp_terrains_path
                self.update_path_labels()
            else:
                messagebox.showerror(self.get_text('error_path_title'), self.get_text('error_path_msg'))

    def switch_mode(self, mode):
        """Αλλάζει μεταξύ των modes Μετακίνησης και Επαναφοράς."""
        self.current_mode = mode
        
        self.move_mode_button.config(style='TButton')
        self.restore_mode_button.config(style='TButton')
        
        self.select_target_button.config(state=tk.DISABLED) 
        self.execute_button.config(state=tk.DISABLED)
        self.progress_bar.config(value=0, mode='determinate') # Επαναφορά μπάρας προόδου
        
        self.map_selection_frame.pack_forget()
        
        if mode == 'move':
            self.move_mode_button.config(style='Accent.TButton')
            self.select_target_button.config(state=tk.NORMAL) 
            self.show_map_selection_view() 
            self.progress_label_main.config(text=self.get_text('progress_select_maps_move'))
        elif mode == 'restore':
            self.restore_mode_button.config(style='Accent.TButton')
            self.show_map_selection_view() 
            self.progress_label_main.config(text=self.get_text('mode_restore')) 
            
        self.update_destination_display()

    def load_maps(self):
        """Βρίσκει μη μετακινημένους (προς μετακίνηση) και ήδη συνδεδεμένους (προς επαναφορά) χάρτες."""
        self.maps.clear()
        self.linked_maps.clear()
        
        if not self.terrains_path or not os.path.exists(self.terrains_path):
            return

        for name in os.listdir(self.terrains_path):
            map_path = os.path.join(self.terrains_path, name)
            if os.path.isdir(map_path) and name not in ['default', 'base']:
                
                junction_target = self.get_junction_target(map_path)
                if junction_target:
                    # Χάρτης για Επαναφορά
                    self.linked_maps[name] = junction_target
                    continue 
                
                # Χάρτης για Μετακίνηση
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(map_path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if not os.path.islink(fp):
                            try:
                                total_size += os.path.getsize(fp)
                            except OSError: 
                                pass
                            
                self.maps[name] = total_size

    def get_junction_target(self, path):
        """Επιστρέφει τον στόχο ενός junction/symlink."""
        try:
            if os.path.islink(path):
                return os.readlink(path)
            
            if os.name == 'nt':
                try:
                    result = subprocess.run(['fsutil', 'reparsepoint', 'query', path], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    match = re.search(r'Substitute Name: (.+)', result.stdout)
                    if match:
                        target = match.group(1).strip()
                        if target.startswith('\\??\\'):
                            target = target[4:]
                        return target.rstrip('\\')
                except Exception:
                    pass
        except Exception:
            pass
        return None

    def show_map_selection_view(self):
        """Εμφανίζει τους διαθέσιμους χάρτες προς Μεταφορά ή Επαναφορά."""
        
        self.execute_button.config(state=tk.DISABLED) 
        
        for widget in self.map_selection_frame.winfo_children():
            widget.destroy()
        self.map_selection_frame.pack(fill='both', expand=True, padx=15, pady=8)
            
        if self.current_mode == 'move':
            map_list = self.maps
            title = self.get_text('maps_title_move')
            if not self.map_vars:
                 self.map_vars = {} 
        elif self.current_mode == 'restore':
            map_list = self.linked_maps
            title = self.get_text('maps_title_restore')
            if not self.restore_map_vars:
                 self.restore_map_vars = {}
        else:
            return

        map_label_frame = ttk.LabelFrame(self.map_selection_frame, text=title, padding="15")
        map_label_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        if not map_list:
            ttk.Label(map_label_frame, text=self.get_text('maps_not_found'), font=('Arial', 11)).pack(pady=20)
            return

        map_canvas = tk.Canvas(map_label_frame, borderwidth=0) 
        map_canvas.pack(side="left", fill="both", expand=True)
        map_scroll = ttk.Scrollbar(map_label_frame, orient="vertical", command=map_canvas.yview)
        map_scroll.pack(side="right", fill="y")
        map_canvas.configure(yscrollcommand=map_scroll.set)
        
        maps_inner_frame = ttk.Frame(map_canvas)
        maps_inner_frame.bind("<Configure>", lambda e: map_canvas.configure(scrollregion = map_canvas.bbox("all")))
        map_canvas.create_window((0, 0), window=maps_inner_frame, anchor="nw")
        
        map_vars_ref = self.map_vars if self.current_mode == 'move' else self.restore_map_vars

        for map_name, data in map_list.items():
            var = tk.BooleanVar(value=map_vars_ref.get(map_name, tk.BooleanVar(value=False)).get()) 
            map_vars_ref[map_name] = var
            var.trace_add('write', self.check_execution_readiness)
            
            if self.current_mode == 'move':
                size_gb = self.bytes_to_gb(data)
                label_text = f"{map_name} ({size_gb:.2f} GB)"
            else: # restore
                label_text = f"{map_name} ({self.get_text('maps_restored')} {os.path.splitdrive(data)[0]})"
            
            frame = ttk.Frame(maps_inner_frame)
            frame.pack(fill='x', pady=3, padx=3)
            ttk.Checkbutton(frame, text=label_text, variable=var).pack(anchor='w')
            
        self.size_label = ttk.Label(map_label_frame, text="", font=('Arial', 11))
        if self.current_mode == 'move':
            self.size_label.pack(anchor='e', pady=8)
        
        self.check_execution_readiness()
        
    def bytes_to_gb(self, size_bytes):
        """Μετατρέπει bytes σε GB."""
        return size_bytes / (1024 ** 3)
        
    def check_execution_readiness(self, *args):
        """Ελέγχει αν έχει επιλεγεί τουλάχιστον ένας χάρτης και ενημερώνει τα βήματα."""
        
        selected_maps = []
        
        if self.current_mode == 'move':
            selected_maps = [name for name, var in self.map_vars.items() if var.get()]
            self.selected_maps_size = sum(self.maps[name] for name in selected_maps)
            
            size_gb = self.bytes_to_gb(self.selected_maps_size)
            if hasattr(self, 'size_label'):
                self.size_label.config(text=f"{self.get_text('maps_size_label')} {size_gb:.2f} GB")
                
            if selected_maps:
                if self.target_path.get() and os.path.isdir(self.target_path.get()):
                    self.execute_button.config(state=tk.NORMAL)
                    self.progress_label_main.config(text=f"{self.get_text('progress_ready_move')} {self.target_path.get()}")
                else:
                    self.execute_button.config(state=tk.DISABLED)
                    self.progress_label_main.config(text=self.get_text('progress_select_dest'))
            else:
                self.execute_button.config(state=tk.DISABLED)
                self.progress_label_main.config(text=self.get_text('progress_select_maps_move'))


        elif self.current_mode == 'restore':
            selected_maps = [name for name, var in self.restore_map_vars.items() if var.get()]
            
            if selected_maps:
                self.execute_button.config(state=tk.NORMAL)
                self.progress_label_main.config(text=self.get_text('progress_ready_restore'))
            else:
                self.execute_button.config(state=tk.DISABLED)
                self.progress_label_main.config(text=self.get_text('mode_restore'))
                
        self.update_destination_display()

    def update_destination_display(self, *args):
        """Ενημερώνει την εμφάνιση της διαδρομής στο GUI και το χρώμα της."""
        path = self.target_path.get()
        
        if self.current_mode == 'move':
            if path:
                self.target_path_display.config(text=path, foreground='green')
            else:
                self.target_path_display.config(text=self.get_text('dest_default_move'), foreground='red')
        elif self.current_mode == 'restore':
            self.target_path_display.config(text=self.get_text('dest_default_restore'), foreground='gray')
        else: 
            self.target_path_display.config(text=self.get_text('dest_default_move'), foreground='red')

    def browse_for_target_path(self):
        """Επιλογή φακέλου προορισμού (Μεταφορά) ΚΑΙ έλεγχος χώρου."""
        
        initial_dir = self.target_path.get() if self.target_path.get() else os.path.expanduser('~')
        
        folder = filedialog.askdirectory(title=self.get_text('dest_button'), initialdir=initial_dir)
        if folder:
            if self.dcs_path and folder.startswith(self.dcs_path):
                messagebox.showwarning(self.get_text('warning_dest_title'), self.get_text('warning_dest_msg'))
                return
            
            selected_maps = [name for name, var in self.map_vars.items() if var.get()]
            if selected_maps:
                try:
                    usage = psutil.disk_usage(os.path.splitdrive(folder)[0])
                    if usage.free < self.selected_maps_size:
                        size_gb = self.bytes_to_gb(self.selected_maps_size)
                        free_gb = self.bytes_to_gb(usage.free)
                        error_msg = f"{self.get_text('error_space_msg')} {size_gb:.2f} GB {self.get_text('error_space_available')} {free_gb:.2f} GB"
                        messagebox.showerror(self.get_text('error_space_title'), error_msg)
                        return
                except Exception as e:
                    messagebox.showerror(self.get_text('exec_disk_error'), f"{e}")
                    
            self.target_path.set(folder)
            
    def start_execution_thread(self):
        """Εκκινεί τη λειτουργία εκτέλεσης σε ξεχωριστό thread."""
        
        self.set_controls_state(tk.DISABLED)
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()

        if self.current_mode == 'move':
            selected_maps = [name for name, var in self.map_vars.items() if var.get()]
            target_base_path = self.target_path.get()
            
            if not selected_maps or not target_base_path:
                self.restore_ui_after_execution(success=False)
                return

            if os.name == 'nt' and not self.is_admin():
                messagebox.showwarning(self.get_text('warning_admin_title'), self.get_text('warning_admin_msg'))

            self.progress_label_main.config(text=self.get_text('exec_moving'))
            thread = threading.Thread(target=self.execute_move, args=(selected_maps, target_base_path))

        elif self.current_mode == 'restore':
            selected_maps = [name for name, var in self.restore_map_vars.items() if var.get()]
            
            if not selected_maps:
                self.restore_ui_after_execution(success=False)
                return
                
            self.progress_label_main.config(text=self.get_text('exec_restoring'))
            thread = threading.Thread(target=self.execute_restore, args=(selected_maps,))

        thread.start()

    def is_admin(self):
        """Ελέγχει αν η εφαρμογή τρέχει ως διαχειριστής (μόνο για Windows)."""
        if os.name == 'nt':
            import ctypes
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        return True 
        
    def set_controls_state(self, state):
        """Απενεργοποιεί/Ενεργοποιεί όλα τα κύρια controls."""
        controls = [
            self.select_dcs_button, self.move_mode_button, self.restore_mode_button,
            self.execute_button, self.select_target_button 
        ]
        for control in controls:
            control.config(state=state)
        
        for widget in self.map_selection_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for child in widget.winfo_children():
                     if isinstance(child, (ttk.Checkbutton, ttk.Button, tk.Canvas)):
                        child.config(state=state)


    def execute_move(self, selected_maps, target_base_path):
        """Εκτελεί τη μετακίνηση των φακέλων και δημιουργεί τους συμβολικούς συνδέσμους (mklink)."""
        source_base_path = self.terrains_path
        success_count = 0
        error_messages = []
        total_maps = len(selected_maps)
        
        try:
            os.makedirs(target_base_path, exist_ok=True)
        except Exception as e:
            error_messages.append(f"{self.get_text('exec_disk_error')}: {e}")
            self.master.after(0, lambda: messagebox.showerror(self.get_text('exec_fail_title'), error_messages[0]))
            self.restore_ui_after_execution(False)
            return

        for i, map_name in enumerate(selected_maps):
            source_map_path = os.path.join(source_base_path, map_name)
            target_map_path = os.path.join(target_base_path, map_name)
            
            # Ενημέρωση προόδου
            self.master.after(0, lambda m=map_name, i=i: self.update_progress(i, total_maps, f"{self.get_text('exec_moving')[:-3]}: {m}")) 

            try:
                if not os.path.exists(target_map_path):
                    shutil.move(source_map_path, target_base_path)
                
                command = f'mklink /J "{source_map_path}" "{target_map_path}"'
                
                subprocess.run(
                    command, 
                    shell=True, 
                    check=True, 
                    capture_output=True, 
                    text=True, 
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                success_count += 1
                
            except subprocess.CalledProcessError as e:
                error_messages.append(f"Σφάλμα mklink/διοίκηση για {map_name}: ({self.get_text('warning_admin_msg')}) ({e.stderr.strip()})")
            except Exception as e:
                error_messages.append(f"Γενικό Σφάλμα για {map_name}: {e}")

        self.restore_ui_after_execution(success=success_count > 0, error_messages=error_messages, mode_text="move")


    def execute_restore(self, selected_maps):
        """Εκτελεί την επαναφορά των χαρτών στην αρχική τους θέση."""
        source_base_path = self.terrains_path 
        success_count = 0
        error_messages = []
        total_maps = len(selected_maps)

        for i, map_name in enumerate(selected_maps):
            source_map_path = os.path.join(source_base_path, map_name) 
            target_map_path_actual = self.linked_maps.get(map_name) 
            
            # Ενημέρωση προόδου
            self.master.after(0, lambda m=map_name, i=i: self.update_progress(i, total_maps, f"{self.get_text('exec_restoring')[:-3]}: {m}"))

            if not target_map_path_actual or not os.path.exists(target_map_path_actual):
                 error_messages.append(f"Σφάλμα για {map_name}: Δεν βρέθηκε ο φάκελος δεδομένων στόχος: {target_map_path_actual}.")
                 continue

            try:
                if os.path.exists(source_map_path) and self.get_junction_target(source_map_path):
                    subprocess.run(
                        f'cmd /C rmdir "{source_map_path}"', 
                        shell=True, 
                        check=True, 
                        capture_output=True, 
                        text=True, 
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                
                shutil.move(target_map_path_actual, source_base_path)
                
                success_count += 1

            except subprocess.CalledProcessError as e:
                error_messages.append(f"Σφάλμα διαγραφής σύνδεσης/διοίκηση για {map_name}: ({self.get_text('warning_admin_msg')}) ({e.stderr.strip()})")
            except Exception as e:
                error_messages.append(f"Γενικό Σφάλμα επαναφοράς για {map_name}: {e}")

        self.restore_ui_after_execution(success=success_count > 0, error_messages=error_messages, mode_text="restore")
        
    def update_progress(self, current, total, text):
        """Ενημερώνει τη γραμμή προόδου και την ετικέτα στο κύριο παράθυρο."""
        progress_value = (current / total) * 100
        self.progress_bar.config(mode='determinate', value=progress_value)
        self.progress_label_main.config(text=f"({current}/{total}) {text}")
        self.master.update_idletasks()

    def show_custom_message(self, title, message, icon):
        """Δημιουργεί ένα μεγαλύτερο και πιο εμφανές παράθυρο μηνύματος (για τέλος διαδικασίας)."""
        
        dialog = tk.Toplevel(self.master)
        dialog.title(title)
        dialog.geometry("500x200") 
        dialog.resizable(False, False)
        dialog.grab_set() 
        
        # Κεντράρισμα του παραθύρου
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - (width // 2)
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - (height // 2)
        dialog.geometry('+%d+%d' % (x, y))
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill='both', expand=True)
        
        # Χρησιμοποιούμε μεγαλύτερη γραμματοσειρά
        ttk.Label(frame, text=title, font=('Arial', 18, 'bold')).pack(pady=(5, 15))
        
        message_label = ttk.Label(frame, text=message, font=('Arial', 14), anchor='center', justify=tk.CENTER)
        message_label.pack(fill='x', pady=10)
        
        # Κουμπί OK
        ttk.Button(frame, text="OK", command=dialog.destroy, style='Accent.TButton' if icon == 'info' else 'TButton', width=10).pack(pady=15)
        
        self.master.wait_window(dialog)
        

    def restore_ui_after_execution(self, success, error_messages=None, mode_text="Λειτουργία"):
        """Επαναφέρει το UI στην αρχική κατάσταση μετά την εκτέλεση."""
        self.master.after(0, self._restore_ui_gui_thread, success, error_messages, mode_text)
        
    def _restore_ui_gui_thread(self, success, error_messages, mode_text):
        """Εκτελείται στο κύριο thread για ενημέρωση GUI."""
        
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate', value=100 if success else 0)
        
        self.load_maps()
        
        # Εμφάνιση μηνυμάτων με το custom dialog (για να είναι πιο εμφανές από το απλό messagebox)
        if error_messages:
            title_key = f'exec_warning_title_{mode_text}' if mode_text in ['move', 'restore'] else 'exec_fail_title'
            title = self.get_text(title_key)
            message = self.get_text('exec_warning_msg_prefix') + "\n".join(error_messages)
            icon = 'warning'
        elif success:
            title_key = f'exec_success_title_{mode_text}' if mode_text in ['move', 'restore'] else 'exec_fail_title'
            title = self.get_text(title_key)
            message = self.get_text('exec_success_msg')
            icon = 'info'
        else:
             title = self.get_text('exec_fail_title')
             message = self.get_text('exec_fail_msg')
             icon = 'error'

        self.show_custom_message(title, message, icon)
        
        # Επαναφορά Controls
        self.set_controls_state(tk.NORMAL)
        self.execute_button.config(state=tk.DISABLED)
        self.progress_label_main.config(text=self.get_text('progress_done'))
        
        self.map_selection_frame.pack_forget()
        if self.current_mode:
            self.switch_mode(self.current_mode)


if __name__ == "__main__":
    if not PILLOW_AVAILABLE:
        print("Προσοχή: Η βιβλιοθήκη Pillow (PIL) δεν βρέθηκε.")
        print("Τα εικονίδια των σημαιών δεν θα εμφανιστούν. Παρακαλώ εκτελέστε: pip install Pillow")
        
    try:
        root = tk.Tk()
        # Ρύθμιση μεγέθους παραθύρου (όπως στην v.1.8)
        root.geometry("1000x1000") 
        root.resizable(True, True) 

        app = DCSMapMoverApp(root)
        
        # Εμφάνιση κύριου παραθύρου μετά τον έλεγχο admin
        if app.master.winfo_exists():
            root.deiconify()
        
        root.mainloop()
    except Exception as e:
        print(f"Σφάλμα εκτέλεσης της εφαρμογής: {e}")
