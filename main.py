import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
from typing import Dict, List, Tuple
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class JudicialAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Judicial Decision Analyzer")
        self.root.geometry("1000x700")
        
        # Data storage
        self.judges_data = {}
        self.current_judge_cases = []
        
        # API Key
        self.api_key = os.getenv('SERPAPI_KEY', '')
        
        # Sample data for demonstration (fallback if API fails)
        self.sample_judges = {
            "California": [
                "Judge Sarah Martinez",
                "Judge Michael Chen",
                "Judge Patricia Williams",
                "Judge Robert Johnson",
                "Judge Lisa Anderson"
            ]
        }
        
        # Sample case data (fallback if API fails)
        self.sample_cases = {
            "Judge Sarah Martinez": [
                {
                    "case_type": "Grand Theft Auto",
                    "verdict": "Guilty",
                    "punishment": "3 Years in Prison",
                    "criminal_history": "1 Felony, 2 Misdemeanors"
                },
                {
                    "case_type": "Burglary",
                    "verdict": "Guilty",
                    "punishment": "5 Years in Prison",
                    "criminal_history": "2 Felonies"
                },
                {
                    "case_type": "Drug Possession",
                    "verdict": "Not Guilty",
                    "punishment": "N/A",
                    "criminal_history": "No Prior Record"
                }
            ],
            "Judge Michael Chen": [
                {
                    "case_type": "Assault",
                    "verdict": "Guilty",
                    "punishment": "2 Years Probation",
                    "criminal_history": "1 Misdemeanor"
                },
                {
                    "case_type": "Fraud",
                    "verdict": "Guilty",
                    "punishment": "18 Months in Prison",
                    "criminal_history": "No Prior Record"
                }
            ]
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # State selection
        ttk.Label(main_frame, text="Select State:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.state_var = tk.StringVar()
        self.state_dropdown = ttk.Combobox(main_frame, textvariable=self.state_var, width=30)
        self.state_dropdown['values'] = ['California']  # Add more states later
        self.state_dropdown.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.state_dropdown.bind('<<ComboboxSelected>>', self.on_state_selected)
        
        # Judge selection
        ttk.Label(main_frame, text="Select Judge:", font=('Arial', 12, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.judge_var = tk.StringVar()
        self.judge_dropdown = ttk.Combobox(main_frame, textvariable=self.judge_var, width=30)
        self.judge_dropdown.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.judge_dropdown.bind('<<ComboboxSelected>>', self.on_judge_selected)
        
        # Fetch data button
        self.fetch_button = ttk.Button(main_frame, text="Fetch Judge Data", command=self.fetch_judge_data)
        self.fetch_button.grid(row=1, column=2, padx=10)
        
        # Case history table
        ttk.Label(main_frame, text="Judge's Case History:", font=('Arial', 14, 'bold')).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(20, 5))
        
        # Create Treeview for case history
        self.tree_frame = ttk.Frame(main_frame)
        self.tree_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=('Case Type', 'Verdict', 'Punishment', 'Criminal History'), show='headings', height=10)
        
        # Define headings
        self.tree.heading('Case Type', text='Case Type')
        self.tree.heading('Verdict', text='Verdict')
        self.tree.heading('Punishment', text='Punishment')
        self.tree.heading('Criminal History', text='Criminal History')
        
        # Column widths
        self.tree.column('Case Type', width=200)
        self.tree.column('Verdict', width=100)
        self.tree.column('Punishment', width=200)
        self.tree.column('Criminal History', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Client case prediction section
        prediction_frame = ttk.LabelFrame(main_frame, text="Case Outcome Prediction", padding="10")
        prediction_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Client criminal history
        ttk.Label(prediction_frame, text="Client's Criminal History:").grid(row=0, column=0, sticky=tk.W, pady=5)
        history_frame = ttk.Frame(prediction_frame)
        history_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(history_frame, text="Felonies:").pack(side=tk.LEFT)
        self.felonies_var = tk.StringVar(value="0")
        self.felonies_spinbox = ttk.Spinbox(history_frame, from_=0, to=10, textvariable=self.felonies_var, width=5)
        self.felonies_spinbox.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(history_frame, text="Misdemeanors:").pack(side=tk.LEFT, padx=(20, 0))
        self.misdemeanors_var = tk.StringVar(value="0")
        self.misdemeanors_spinbox = ttk.Spinbox(history_frame, from_=0, to=20, textvariable=self.misdemeanors_var, width=5)
        self.misdemeanors_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Case type
        ttk.Label(prediction_frame, text="Case Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.case_type_var = tk.StringVar()
        self.case_type_dropdown = ttk.Combobox(prediction_frame, textvariable=self.case_type_var, width=30)
        self.case_type_dropdown['values'] = ['Grand Theft Auto', 'Burglary', 'Drug Possession', 'Assault', 'Fraud', 'DUI', 'Robbery']
        self.case_type_dropdown.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Predict button
        self.predict_button = ttk.Button(prediction_frame, text="Predict Outcome", command=self.predict_outcome)
        self.predict_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Prediction results
        self.results_text = tk.Text(prediction_frame, height=6, width=70, wrap=tk.WORD)
        self.results_text.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. API Key: " + ("Loaded ✓" if self.api_key else "Not Found ✗"))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
    def on_state_selected(self, event):
        selected_state = self.state_var.get()
        if selected_state in self.sample_judges:
            self.judge_dropdown['values'] = self.sample_judges[selected_state]
            self.judge_dropdown.set('')
            self.clear_case_history()
            
    def on_judge_selected(self, event):
        self.clear_case_history()
        
    def fetch_judge_data(self):
        judge_name = self.judge_var.get()
        if not judge_name:
            messagebox.showwarning("Warning", "Please select a judge first!")
            return
        
        self.status_var.set("Fetching data from Google Scholar...")
        self.root.update()
        
        # Try to fetch real data from Google Scholar
        real_data = self.fetch_from_google_scholar(judge_name, self.state_var.get())
        
        if real_data:
            self.current_judge_cases = real_data
            self.status_var.set(f"Loaded {len(real_data)} cases from Google Scholar")
        else:
            # Fall back to sample data
            if judge_name in self.sample_cases:
                self.current_judge_cases = self.sample_cases[judge_name]
                self.status_var.set("Using sample data (API call failed)")
            else:
                # Generate generic sample data
                self.current_judge_cases = [
                    {
                        "case_type": "Various Offenses",
                        "verdict": "Mixed",
                        "punishment": "Varies",
                        "criminal_history": "Varies"
                    }
                ]
                self.status_var.set("Using generic sample data")
        
        self.display_case_history()
            
    def clear_case_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
    def display_case_history(self):
        self.clear_case_history()
        for case in self.current_judge_cases:
            self.tree.insert('', 'end', values=(
                case['case_type'],
                case['verdict'],
                case['punishment'],
                case['criminal_history']
            ))
            
    def predict_outcome(self):
        judge_name = self.judge_var.get()
        case_type = self.case_type_var.get()
        felonies = int(self.felonies_var.get())
        misdemeanors = int(self.misdemeanors_var.get())
        
        if not judge_name or not case_type:
            messagebox.showwarning("Warning", "Please select a judge and case type!")
            return
            
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Simple prediction logic (in production, use ML model)
        guilty_rate = self.calculate_guilty_rate()
        severity_score = self.calculate_severity_score(felonies, misdemeanors)
        
        prediction_text = f"Prediction Analysis for {judge_name}\n"
        prediction_text += f"Case Type: {case_type}\n"
        prediction_text += f"Client Criminal History: {felonies} Felonies, {misdemeanors} Misdemeanors\n\n"
        
        if guilty_rate > 0.7 and severity_score > 5:
            prediction_text += "⚠️ HIGH RISK: Based on historical data, this judge has a high conviction rate ({}%) ".format(int(guilty_rate * 100))
            prediction_text += "and tends to give harsher sentences for repeat offenders.\n"
            prediction_text += "Recommended: Consider plea bargaining or alternative dispute resolution."
        elif guilty_rate > 0.5:
            prediction_text += "⚡ MODERATE RISK: This judge has a moderate conviction rate ({}%) ".format(int(guilty_rate * 100))
            prediction_text += "with balanced sentencing patterns.\n"
            prediction_text += "Recommended: Prepare strong defense with character witnesses."
        else:
            prediction_text += "✅ LOWER RISK: This judge has shown leniency in similar cases ({}% conviction rate).\n".format(int(guilty_rate * 100))
            prediction_text += "Recommended: Focus on rehabilitation and community service arguments."
            
        self.results_text.insert(tk.END, prediction_text)
        
    def calculate_guilty_rate(self):
        if not self.current_judge_cases:
            return 0.5
        guilty_count = sum(1 for case in self.current_judge_cases if case['verdict'] == 'Guilty')
        return guilty_count / len(self.current_judge_cases)
        
    def calculate_severity_score(self, felonies, misdemeanors):
        return (felonies * 3) + (misdemeanors * 1)
        
    def fetch_from_google_scholar(self, judge_name, state):
        """
        Fetch judge data from Google Scholar API
        """
        if not self.api_key:
            messagebox.showerror("Error", "Please set your SERPAPI_KEY in the .env file!")
            return None
            
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_scholar",
            "q": f'"{judge_name}" "{state} court" criminal case verdict',
            "api_key": self.api_key,
            "num": "20"  # Get up to 20 results
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if "error" in data:
                messagebox.showerror("API Error", f"SerpAPI Error: {data['error']}")
                return None
            
            # Parse the results
            cases = []
            organic_results = data.get("organic_results", [])
            
            for result in organic_results:
                # Extract case information from title and snippet
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                
                # Parse case type from title/snippet
                case_type = self.extract_case_type(title + " " + snippet)
                
                # Parse verdict
                verdict = self.extract_verdict(title + " " + snippet)
                
                # Parse punishment
                punishment = self.extract_punishment(title + " " + snippet)
                
                # Criminal history (harder to extract, so we'll use a placeholder)
                criminal_history = "Not Available"
                
                cases.append({
                    "case_type": case_type,
                    "verdict": verdict,
                    "punishment": punishment,
                    "criminal_history": criminal_history
                })
            
            if not cases:
                messagebox.showinfo("No Results", f"No cases found for {judge_name} in Google Scholar. Using sample data.")
                return None
                
            return cases[:10]  # Return up to 10 cases
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network Error", f"Failed to connect to SerpAPI: {str(e)}")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {str(e)}")
            return None
    
    def extract_case_type(self, text):
        """Extract case type from text"""
        case_types = {
            'murder': 'Murder',
            'homicide': 'Homicide',
            'assault': 'Assault',
            'battery': 'Battery',
            'theft': 'Theft',
            'burglary': 'Burglary',
            'robbery': 'Robbery',
            'drug': 'Drug Offense',
            'narcotic': 'Drug Offense',
            'fraud': 'Fraud',
            'embezzlement': 'Embezzlement',
            'dui': 'DUI',
            'dwi': 'DUI',
            'domestic': 'Domestic Violence',
            'sexual': 'Sexual Offense',
            'arson': 'Arson',
            'vandalism': 'Vandalism',
            'weapon': 'Weapons Charge'
        }
        
        text_lower = text.lower()
        for keyword, case_type in case_types.items():
            if keyword in text_lower:
                return case_type
        
        return "Criminal Case"
    
    def extract_verdict(self, text):
        """Extract verdict from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['guilty', 'convicted', 'conviction']):
            return "Guilty"
        elif any(word in text_lower for word in ['not guilty', 'acquitted', 'acquittal', 'dismissed']):
            return "Not Guilty"
        elif any(word in text_lower for word in ['plea', 'plead', 'pled']):
            return "Plea Deal"
        
        return "Unknown"
    
    def extract_punishment(self, text):
        """Extract punishment from text"""
        import re
        
        # Look for prison/jail sentences
        prison_match = re.search(r'(\d+)\s*(year|month|day)s?\s*(in\s*)?(prison|jail|incarceration)', text, re.IGNORECASE)
        if prison_match:
            return f"{prison_match.group(1)} {prison_match.group(2)}s in prison"
        
        # Look for probation
        probation_match = re.search(r'(\d+)\s*(year|month)s?\s*(of\s*)?probation', text, re.IGNORECASE)
        if probation_match:
            return f"{probation_match.group(1)} {probation_match.group(2)}s probation"
        
        # Look for fines
        fine_match = re.search(r'\$[\d,]+\s*fine', text, re.IGNORECASE)
        if fine_match:
            return fine_match.group(0)
        
        if "life" in text.lower() and ("prison" in text.lower() or "sentence" in text.lower()):
            return "Life in prison"
        
        return "Not specified"

def main():
    root = tk.Tk()
    app = JudicialAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
