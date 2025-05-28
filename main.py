"""
Criminal Case Outcome Predictor - Main Application
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from collections import defaultdict
import config

# Import our modules
from gui_components import SearchFrame, ClientFrame, ResultsNotebook
from database_builder import DatabaseBuilder
from analyzer import CaseAnalyzer


class JudicialAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Criminal Case Outcome Predictor")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        
        # Data storage
        self.case_database = []
        self.judges_data = defaultdict(list)
        self.available_judges = []
        
        # Initialize components
        self.db_builder = DatabaseBuilder()
        self.analyzer = CaseAnalyzer()
        
        # Check API key
        self.has_api_key = bool(self.db_builder.api_key)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Search section
        self.search_frame = SearchFrame(main_frame)
        self.search_frame.search_judges_button.configure(command=self.search_for_judges)
        self.search_frame.build_button.configure(command=self.build_case_database)
        self.search_frame.state_dropdown.bind('<<ComboboxSelected>>', self.on_state_selected)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Client information section (optional)
        self.client_frame = ClientFrame(main_frame)
        self.client_frame.analyze_button.configure(command=self.analyze_case)
        
        # Results section
        self.results = ResultsNotebook(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. API Key: " + ("Loaded ✓" if self.has_api_key else "Not Found ✗"))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def on_state_selected(self, event):
        """Clear judge dropdown when state changes"""
        self.search_frame.judge_dropdown.set("Select a judge...")
        self.search_frame.judge_dropdown['values'] = []
        self.available_judges = []
        
    def search_for_judges(self):
        """Search for judges in the selected state"""
        if not self.has_api_key:
            messagebox.showerror("Error", "Please set your SERPAPI_KEY in the .env file!")
            return
        
        state = self.search_frame.state_var.get()
        if not state:
            messagebox.showwarning("Warning", "Please select a state first!")
            return
        
        # Run in background thread
        thread = threading.Thread(target=self._search_judges_thread, args=(state,))
        thread.daemon = True
        thread.start()
    
    def _search_judges_thread(self, state):
        """Background thread to search for judges"""
        self.root.after(0, lambda: self.progress.configure(mode='indeterminate'))
        self.root.after(0, self.progress.start)
        self.root.after(0, lambda: self.status_var.set(f"Searching for judges in {state}..."))
        
        try:
            # This will search for judges and extract their names
            judges = self.db_builder.search_judges_in_state(state)
            self.available_judges = judges
            
            # Update UI
            self.root.after(0, lambda: self.search_frame.judge_dropdown.configure(values=judges))
            if judges:
                self.root.after(0, lambda: self.status_var.set(f"Found {len(judges)} judges in {state}"))
                self.root.after(0, lambda: self.search_frame.judge_dropdown.set("Select a judge..."))
            else:
                self.root.after(0, lambda: self.status_var.set(f"No judges found in {state}"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to search for judges: {str(e)}"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.progress.configure(mode='determinate'))
        
    def build_case_database(self):
        """Build database of criminal cases for selected judge"""
        if not self.has_api_key:
            messagebox.showerror("Error", "Please set your SERPAPI_KEY in the .env file!")
            return
        
        judge = self.search_frame.judge_var.get()
        if not judge or judge == "Select a judge...":
            messagebox.showwarning("Warning", "Please select a judge first!")
            return
        
        # Run in background thread
        thread = threading.Thread(target=self._build_database_thread)
        thread.daemon = True
        thread.start()
        
    def _build_database_thread(self):
        """Background thread to build case database"""
        # Get parameters
        state = self.search_frame.state_var.get()
        judge = self.search_frame.judge_var.get()
        num_cases = int(self.search_frame.num_cases_var.get())
        
        # Setup progress
        self.root.after(0, lambda: self.progress.configure(maximum=num_cases, value=0))
        self.root.after(0, lambda: self.status_var.set(f"Building case database for {judge}..."))
        
        # Build database
        try:
            self.case_database = self.db_builder.build_judge_database(
                state, 
                judge,
                num_cases,
                progress_callback=lambda v: self.root.after(0, lambda: self.progress.configure(value=v))
            )
            
            # Display all cases immediately in the Similar Cases tab
            self.root.after(0, lambda: self.display_judge_cases())
            
            # Update status
            self.root.after(0, lambda: self.status_var.set(
                f"Found {len(self.case_database)} cases for {judge}"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to build database: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.progress.configure(value=0))
    
    def display_judge_cases(self):
        """Display all cases for the selected judge"""
        self.results.clear_similar_cases()
        
        # Add all cases for this judge
        for case in self.case_database[:config.MAX_SIMILAR_CASES_DISPLAY]:
            self.results.add_similar_case((
                case['defendant'],
                case['criminal_history'],
                case['charge'],
                case['verdict'],
                case['sentence'],
                self.search_frame.judge_var.get()  # Use selected judge name
            ))
        
        # Generate judge statistics
        judge_stats = self.analyzer.generate_single_judge_stats(
            self.search_frame.judge_var.get(), 
            self.case_database
        )
        self.results.set_judge_stats_text(judge_stats)
    
    def analyze_case(self):
        """Analyze client's case based on judge's history"""
        if not self.case_database:
            messagebox.showwarning("Warning", "Please build the case database first!")
            return
        
        if not self.client_frame.case_type_var.get():
            messagebox.showwarning("Warning", "Please select the current charge!")
            return
        
        # Get client info
        client_info = {
            'felonies': int(self.client_frame.felonies_var.get()),
            'misdemeanors': int(self.client_frame.misdemeanors_var.get()),
            'convictions': int(self.client_frame.convictions_var.get()),
            'charge': self.client_frame.case_type_var.get(),
            'judge': self.search_frame.judge_var.get()  # Use selected judge
        }
        
        # Find similar cases
        similar_cases = self.analyzer.find_similar_cases(self.case_database, client_info)
        
        # Display prediction
        self.display_prediction(client_info)
        
    def display_prediction(self, client_info):
        """Display prediction analysis"""
        report = self.analyzer.generate_prediction_report(client_info)
        self.results.set_prediction_text(report)


def main():
    root = tk.Tk()
    app = JudicialAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()


def main():
    root = tk.Tk()
    app = JudicialAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()



import tkinter as tk
from tkinter import ttk, messagebox
import threading
from collections import defaultdict

# Import our modules
from gui_components import SearchFrame, ClientFrame, ResultsNotebook
from database_builder import DatabaseBuilder
from analyzer import CaseAnalyzer


class JudicialAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Criminal Case Outcome Predictor")
        self.root.geometry("1200x800")
        
        # Data storage
        self.case_database = []
        self.judges_data = defaultdict(list)
        
        # Initialize components
        self.db_builder = DatabaseBuilder()
        self.analyzer = CaseAnalyzer()
        
        # Check API key
        self.has_api_key = bool(self.db_builder.api_key)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Search section
        self.search_frame = SearchFrame(main_frame)
        self.search_frame.search_button.configure(command=self.build_case_database)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Client information section
        self.client_frame = ClientFrame(main_frame)
        self.client_frame.analyze_button.configure(command=self.analyze_case)
        
        # Results section
        self.results = ResultsNotebook(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. API Key: " + ("Loaded ✓" if self.has_api_key else "Not Found ✗"))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
    def build_case_database(self):
        """Build database of criminal cases"""
        if not self.has_api_key:
            messagebox.showerror("Error", "Please set your SERPAPI_KEY in the .env file!")
            return
        
        # Run in background thread
        thread = threading.Thread(target=self._build_database_thread)
        thread.daemon = True
        thread.start()
        
    def _build_database_thread(self):
        """Background thread to build case database"""
        # Get parameters
        state = self.search_frame.state_var.get()
        case_type_filter = self.search_frame.case_type_var.get()
        num_cases = int(self.search_frame.num_cases_var.get())
        
        # Setup progress
        self.root.after(0, lambda: self.progress.configure(maximum=num_cases, value=0))
        self.root.after(0, lambda: self.status_var.set("Building criminal case database..."))
        
        # Build database
        try:
            self.case_database, judges_dict = self.db_builder.build_database(
                state, 
                case_type_filter, 
                num_cases,
                progress_callback=lambda v: self.root.after(0, lambda: self.progress.configure(value=v))
            )
            
            # Convert judges_dict to defaultdict
            self.judges_data = defaultdict(list, judges_dict)
            
            # Update judge dropdown
            judge_names = sorted(list(judges_dict.keys()))
            self.root.after(0, lambda: self.client_frame.judge_dropdown.configure(values=judge_names))
            
            # Update status
            self.root.after(0, lambda: self.status_var.set(
                f"Database built: {len(self.case_database)} cases, {len(judge_names)} judges"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to build database: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.progress.configure(value=0))
    
    def analyze_case(self):
        """Analyze client's case based on similar cases"""
        if not self.case_database:
            messagebox.showwarning("Warning", "Please build the case database first!")
            return
        
        if not self.client_frame.case_type_var.get():
            messagebox.showwarning("Warning", "Please select the current charge!")
            return
        
        # Get client info
        client_info = {
            'felonies': int(self.client_frame.felonies_var.get()),
            'misdemeanors': int(self.client_frame.misdemeanors_var.get()),
            'convictions': int(self.client_frame.convictions_var.get()),
            'charge': self.client_frame.case_type_var.get(),
            'judge': self.client_frame.judge_var.get() or None
        }
        
        # Find similar cases
        similar_cases = self.analyzer.find_similar_cases(self.case_database, client_info)
        
        # Display results
        self.display_similar_cases(similar_cases)
        self.display_prediction(client_info)
        self.display_judge_stats()
        
    def display_similar_cases(self, cases):
        """Display similar cases in the table"""
        self.results.clear_similar_cases()
        
        # Add top 20 cases
        for case in cases[:20]:
            self.results.add_similar_case((
                case['defendant'],
                case['criminal_history'],
                case['charge'],
                case['verdict'],
                case['sentence'],
                case['judge']
            ))
    
    def display_prediction(self, client_info):
        """Display prediction analysis"""
        report = self.analyzer.generate_prediction_report(client_info)
        self.results.set_prediction_text(report)
    
    def display_judge_stats(self):
        """Display judge statistics"""
        stats = self.analyzer.generate_judge_statistics(self.judges_data)
        self.results.set_judge_stats_text(stats)


def main():
    root = tk.Tk()
    app = JudicialAnalyzer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
