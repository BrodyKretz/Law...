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
import threading

# Load environment variables
load_dotenv()

class JudicialAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Judicial Decision Analyzer")
        self.root.geometry("1000x750")
        
        # Data storage
        self.judges_data = {}
        self.current_judge_cases = []
        self.found_judges = []
        
        # API Key
        self.api_key = os.getenv('SERPAPI_KEY', '')
        print(f"API Key loaded: {'Yes' if self.api_key else 'No'}")
        
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
        
        # Search for judges button
        self.search_judges_button = ttk.Button(main_frame, text="Search for Judges", command=self.search_for_judges)
        self.search_judges_button.grid(row=0, column=2, padx=10)
        
        # Fetch data button
        self.fetch_button = ttk.Button(main_frame, text="Fetch Judge Data", command=self.fetch_judge_data)
        self.fetch_button.grid(row=1, column=2, padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Case history table
        ttk.Label(main_frame, text="Judge's Case History:", font=('Arial', 14, 'bold')).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(20, 5))
        
        # Create Treeview for case history
        self.tree_frame = ttk.Frame(main_frame)
        self.tree_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=('Case Type', 'Verdict', 'Punishment', 'Source'), show='headings', height=10)
        
        # Define headings
        self.tree.heading('Case Type', text='Case Type')
        self.tree.heading('Verdict', text='Verdict')
        self.tree.heading('Punishment', text='Punishment')
        self.tree.heading('Source', text='Source')
        
        # Column widths
        self.tree.column('Case Type', width=200)
        self.tree.column('Verdict', width=100)
        self.tree.column('Punishment', width=200)
        self.tree.column('Source', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Client case prediction section
        prediction_frame = ttk.LabelFrame(main_frame, text="Case Outcome Prediction", padding="10")
        prediction_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
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
        self.case_type_dropdown['values'] = ['Grand Theft Auto', 'Burglary', 'Drug Possession', 'Assault', 'Fraud', 'DUI', 'Robbery', 'Murder', 'Domestic Violence']
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
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def on_state_selected(self, event):
        self.judge_dropdown.set('')
        self.judge_dropdown['values'] = []
        self.clear_case_history()
        self.status_var.set("Click 'Search for Judges' to find judges in " + self.state_var.get())
        
    def on_judge_selected(self, event):
        self.clear_case_history()
        
    def search_for_judges(self):
        """Search Google Scholar for judges in the selected state"""
        state = self.state_var.get()
        if not state:
            messagebox.showwarning("Warning", "Please select a state first!")
            return
            
        if not self.api_key:
            messagebox.showerror("Error", "Please set your SERPAPI_KEY in the .env file!")
            return
        
        # Run search in background thread
        thread = threading.Thread(target=self._search_judges_thread, args=(state,))
        thread.daemon = True
        thread.start()
        
    def _search_judges_thread(self, state):
        """Background thread to search for judges"""
        self.root.after(0, self.progress.start)
        self.root.after(0, lambda: self.status_var.set(f"Searching for judges in {state}..."))
        
        try:
            # Search for various court types
            judge_names = set()
            court_types = [
                "Superior Court",
                "District Court",
                "Appeals Court",
                "Supreme Court",
                "Criminal Court"
            ]
            
            for court_type in court_types:
                url = "https://serpapi.com/search"
                params = {
                    "engine": "google_scholar",
                    "q": f'"{state} {court_type}" "Judge" criminal case verdict -book -review',
                    "api_key": self.api_key,
                    "num": "20"
                }
                
                try:
                    response = requests.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract judge names from results
                        for result in data.get("organic_results", []):
                            title = result.get("title", "")
                            snippet = result.get("snippet", "")
                            text = title + " " + snippet
                            
                            # Look for judge names
                            judge_patterns = [
                                r"Judge\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
                                r"Justice\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
                                r"Hon\.\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
                                r"Honorable\s+([A-Z][a-z]+\s+[A-Z][a-z]+)"
                            ]
                            
                            for pattern in judge_patterns:
                                matches = re.findall(pattern, text)
                                for match in matches:
                                    if match and len(match.split()) >= 2:
                                        judge_names.add(f"Judge {match}")
                                        
                except Exception as e:
                    print(f"Error searching {court_type}: {e}")
                    continue
            
            # Update UI in main thread
            self.found_judges = sorted(list(judge_names))
            self.root.after(0, self._update_judge_dropdown)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to search for judges: {str(e)}"))
        finally:
            self.root.after(0, self.progress.stop)
            
    def _update_judge_dropdown(self):
        """Update judge dropdown with found judges"""
        if self.found_judges:
            self.judge_dropdown['values'] = self.found_judges
            self.status_var.set(f"Found {len(self.found_judges)} judges. Select one to fetch their cases.")
        else:
            # If no judges found, search for any criminal cases in the state
            self.judge_dropdown['values'] = ["Search All Criminal Cases"]
            self.status_var.set("No specific judges found. You can search all criminal cases.")
        
    def fetch_judge_data(self):
        judge_name = self.judge_var.get()
        if not judge_name:
            messagebox.showwarning("Warning", "Please select a judge first!")
            return
        
        # Run fetch in background thread
        thread = threading.Thread(target=self._fetch_judge_data_thread, args=(judge_name,))
        thread.daemon = True
        thread.start()
        
    def _fetch_judge_data_thread(self, judge_name):
        """Background thread to fetch judge data"""
        self.root.after(0, self.progress.start)
        self.root.after(0, lambda: self.status_var.set(f"Fetching cases for {judge_name}..."))
        
        try:
            # Fetch real data from Google Scholar
            real_data = self.fetch_from_google_scholar(judge_name, self.state_var.get())
            
            if real_data:
                self.current_judge_cases = real_data
                self.root.after(0, lambda: self.status_var.set(f"Found {len(real_data)} cases"))
                self.root.after(0, self.display_case_history)
            else:
                self.root.after(0, lambda: self.status_var.set("No cases found"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch data: {str(e)}"))
        finally:
            self.root.after(0, self.progress.stop)
            
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
                case.get('source', 'Google Scholar')
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
        
        # Simple prediction logic
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
            return None
        
        url = "https://serpapi.com/search"
        
        # If searching all cases, modify query
        if judge_name == "Search All Criminal Cases":
            query = f'"{state}" criminal case verdict sentence "guilty OR not guilty"'
        else:
            query = f'"{judge_name}" "{state}" criminal case verdict sentence'
        
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": self.api_key,
            "num": "40"  # Get more results
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if "error" in data:
                return None
            
            # Parse the results
            cases = []
            organic_results = data.get("organic_results", [])
            
            for result in organic_results:
                # Extract case information
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                # Parse case type
                case_type = self.extract_case_type(title + " " + snippet)
                
                # Parse verdict
                verdict = self.extract_verdict(title + " " + snippet)
                
                # Parse punishment
                punishment = self.extract_punishment(title + " " + snippet)
                
                # Only add if we found meaningful data
                if verdict != "Unknown" or punishment != "Not specified":
                    cases.append({
                        "case_type": case_type,
                        "verdict": verdict,
                        "punishment": punishment,
                        "source": title[:50] + "..." if len(title) > 50 else title
                    })
            
            return cases if cases else None
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def extract_case_type(self, text):
        """Extract case type from text"""
        case_types = {
            'murder': 'Murder',
            'homicide': 'Homicide',
            'manslaughter': 'Manslaughter',
            'assault': 'Assault',
            'battery': 'Battery',
            'theft': 'Theft',
            'larceny': 'Larceny',
            'burglary': 'Burglary',
            'robbery': 'Robbery',
            'drug': 'Drug Offense',
            'narcotic': 'Drug Offense',
            'possession': 'Drug Possession',
            'trafficking': 'Drug Trafficking',
            'fraud': 'Fraud',
            'embezzlement': 'Embezzlement',
            'dui': 'DUI',
            'dwi': 'DUI',
            'domestic': 'Domestic Violence',
            'sexual': 'Sexual Offense',
            'rape': 'Sexual Assault',
            'arson': 'Arson',
            'vandalism': 'Vandalism',
            'weapon': 'Weapons Charge',
            'firearm': 'Weapons Charge',
            'kidnapping': 'Kidnapping',
            'conspiracy': 'Conspiracy'
        }
        
        text_lower = text.lower()
        for keyword, case_type in case_types.items():
            if keyword in text_lower:
                return case_type
        
        return "Criminal Case"
    
    def extract_verdict(self, text):
        """Extract verdict from text"""
        text_lower = text.lower()
        
        # Look for guilty verdicts
        if any(word in text_lower for word in ['guilty', 'convicted', 'conviction', 'found guilty']):
            return "Guilty"
        elif any(word in text_lower for word in ['not guilty', 'acquitted', 'acquittal', 'dismissed', 'charges dropped']):
            return "Not Guilty"
        elif any(word in text_lower for word in ['plea', 'plead', 'pled', 'plea bargain', 'plea deal']):
            return "Plea Deal"
        elif 'mistrial' in text_lower:
            return "Mistrial"
        
        return "Unknown"
    
    def extract_punishment(self, text):
        """Extract punishment from text"""
        import re
        
        # Look for death penalty
        if any(phrase in text.lower() for phrase in ['death penalty', 'death sentence', 'capital punishment']):
            return "Death Penalty"
        
        # Look for life sentences
        if any(phrase in text.lower() for phrase in ['life in prison', 'life sentence', 'life without parole']):
            return "Life in Prison"
        
        # Look for specific prison/jail sentences
        prison_patterns = [
            r'(\d+)\s*(?:to\s*)?(\d+)?\s*(year|month|day)s?\s*(?:in\s*)?(?:state\s*)?(?:prison|jail|incarceration)',
            r'sentenced?\s*to\s*(\d+)\s*(year|month|day)s?',
            r'(\d+)\s*(year|month|day)s?\s*(?:prison|jail)\s*(?:sentence|term)'
        ]
        
        for pattern in prison_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        # Look for probation
        probation_match = re.search(r'(\d+)\s*(year|month)s?\s*(?:of\s*)?probation', text, re.IGNORECASE)
        if probation_match:
            return probation_match.group(0)
        
        # Look for fines
        fine_match = re.search(r'\$[\d,]+(?:\.\d{2})?\s*(?:fine|penalty|restitution)', text, re.IGNORECASE)
        if fine_match:
            return fine_match.group(0)
        
        # Look for community service
        service_match = re.search(r'(\d+)\s*hours?\s*(?:of\s*)?community\s*service', text, re.IGNORECASE)
        if service_match:
            return service_match.group(0)
        
        return "Not specified"

def main():
    root = tk.Tk()
    app = JudicialAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
