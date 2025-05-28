"""
GUI components for the Criminal Case Outcome Predictor
"""
import tkinter as tk
from tkinter import ttk
import config

class SearchFrame:
    """Database search controls"""
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Search Criminal Cases Database", padding="10")
        self.frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # State selection
        ttk.Label(self.frame, text="State:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.state_var = tk.StringVar(value="California")
        self.state_dropdown = ttk.Combobox(self.frame, textvariable=self.state_var, width=20)
        self.state_dropdown['values'] = config.STATES
        self.state_dropdown.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Judge selection
        ttk.Label(self.frame, text="Judge:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20,0))
        self.judge_var = tk.StringVar()
        self.judge_dropdown = ttk.Combobox(self.frame, textvariable=self.judge_var, width=30, state="readonly")
        self.judge_dropdown.grid(row=0, column=3, sticky=tk.W, pady=5, padx=5)
        self.judge_dropdown.set("Select state first...")
        
        # Number of cases to fetch
        ttk.Label(self.frame, text="Cases to Analyze:").grid(row=0, column=4, sticky=tk.W, pady=5, padx=(20,0))
        self.num_cases_var = tk.StringVar(value=str(config.DEFAULT_NUM_CASES))
        self.num_cases_spinbox = ttk.Spinbox(
            self.frame, 
            from_=config.MIN_CASES, 
            to=config.MAX_CASES, 
            textvariable=self.num_cases_var, 
            width=10
        )
        self.num_cases_spinbox.grid(row=0, column=5, sticky=tk.W, pady=5, padx=5)
        
        # Build database button
        self.build_button = ttk.Button(self.frame, text="Build Case Database")
        self.build_button.grid(row=0, column=6, padx=20)


class ClientFrame:
    """Client information input controls (optional)"""
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Client Analysis (Optional)", padding="10")
        self.frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Add note about optional nature
        note_label = ttk.Label(self.frame, text="Enter client information to see how they might fare before this judge:", 
                              font=('Arial', 10, 'italic'))
        note_label.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        # Client criminal history
        history_frame = ttk.Frame(self.frame)
        history_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        ttk.Label(history_frame, text="Prior Felonies:").pack(side=tk.LEFT)
        self.felonies_var = tk.StringVar(value="0")
        self.felonies_spinbox = ttk.Spinbox(history_frame, from_=0, to=20, textvariable=self.felonies_var, width=5)
        self.felonies_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(history_frame, text="Prior Misdemeanors:").pack(side=tk.LEFT, padx=(20, 0))
        self.misdemeanors_var = tk.StringVar(value="0")
        self.misdemeanors_spinbox = ttk.Spinbox(history_frame, from_=0, to=50, textvariable=self.misdemeanors_var, width=5)
        self.misdemeanors_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(history_frame, text="Prior Convictions:").pack(side=tk.LEFT, padx=(20, 0))
        self.convictions_var = tk.StringVar(value="0")
        self.convictions_spinbox = ttk.Spinbox(history_frame, from_=0, to=20, textvariable=self.convictions_var, width=5)
        self.convictions_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Current charge
        ttk.Label(self.frame, text="Current Charge:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.case_type_var = tk.StringVar()
        self.case_type_dropdown = ttk.Combobox(self.frame, textvariable=self.case_type_var, width=25)
        self.case_type_dropdown['values'] = config.CHARGE_TYPES
        self.case_type_dropdown.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Analyze button
        self.analyze_button = ttk.Button(self.frame, text="Analyze Client Outcome")
        self.analyze_button.grid(row=3, column=0, columnspan=2, pady=10)


class ResultsNotebook:
    """Tabbed results display"""
    def __init__(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Tab 1: Similar Cases
        self.similar_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.similar_frame, text="Similar Cases")
        
        # Similar cases table
        self.tree_frame = ttk.Frame(self.similar_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=('Defendant', 'Criminal History', 'Charge', 'Verdict', 'Sentence', 'Judge'), 
                                show='headings', height=12)
        
        # Define headings
        self.tree.heading('Defendant', text='Defendant')
        self.tree.heading('Criminal History', text='Criminal History')
        self.tree.heading('Charge', text='Charge')
        self.tree.heading('Verdict', text='Verdict')
        self.tree.heading('Sentence', text='Sentence')
        self.tree.heading('Judge', text='Judge')
        
        # Column widths
        self.tree.column('Defendant', width=150)
        self.tree.column('Criminal History', width=200)
        self.tree.column('Charge', width=150)
        self.tree.column('Verdict', width=100)
        self.tree.column('Sentence', width=150)
        self.tree.column('Judge', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tab 2: Prediction Analysis
        self.prediction_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.prediction_frame, text="Prediction Analysis")
        
        # Prediction results
        self.results_text = tk.Text(self.prediction_frame, height=20, width=80, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 3: Judge Statistics
        self.judge_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.judge_frame, text="Judge Statistics")
        
        self.judge_stats_text = tk.Text(self.judge_frame, height=20, width=80, wrap=tk.WORD)
        self.judge_stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def clear_similar_cases(self):
        """Clear the similar cases tree"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def add_similar_case(self, case_data):
        """Add a case to the similar cases tree"""
        self.tree.insert('', 'end', values=case_data)
    
    def set_prediction_text(self, text):
        """Set the prediction analysis text"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
    
    def set_judge_stats_text(self, text):
        """Set the judge statistics text"""
        self.judge_stats_text.delete(1.0, tk.END)
        self.judge_stats_text.insert(tk.END, text)
