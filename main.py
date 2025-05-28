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
from collections import defaultdict

# Load environment variables
load_dotenv()

class JudicialAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Criminal Case Outcome Predictor")
        self.root.geometry("1200x800")
        
        # Data storage
        self.case_database = []  # All cases found
        self.similar_cases = []  # Cases similar to client
        self.judges_data = defaultdict(list)  # Judge -> cases mapping
        
        # API Key
        self.api_key = os.getenv('SERPAPI_KEY', '')
        print(f"API Key loaded: {'Yes' if self.api_key else 'No'}")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Search Section
        search_frame = ttk.LabelFrame(main_frame, text="Search Criminal Cases Database", padding="10")
        search_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # State selection
        ttk.Label(search_frame, text="State:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.state_var = tk.StringVar(value="California")
        self.state_dropdown = ttk.Combobox(search_frame, textvariable=self.state_var, width=20)
        self.state_dropdown['values'] = ['California', 'New York', 'Texas', 'Florida', 'Illinois']
        self.state_dropdown.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Case type filter
        ttk.Label(search_frame, text="Case Type:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20,0))
        self.search_case_type_var = tk.StringVar(value="All")
        self.search_case_type_dropdown = ttk.Combobox(search_frame, textvariable=self.search_case_type_var, width=20)
        self.search_case_type_dropdown['values'] = ['All', 'Theft', 'Drug Offense', 'Assault', 'DUI', 'Fraud', 'Burglary', 'Robbery', 'Murder']
        self.search_case_type_dropdown.grid(row=0, column=3, sticky=tk.W, pady=5, padx=5)
        
        # Number of cases to fetch
        ttk.Label(search_frame, text="Cases to Analyze:").grid(row=0, column=4, sticky=tk.W, pady=5, padx=(20,0))
        self.num_cases_var = tk.StringVar(value="50")
        self.num_cases_spinbox = ttk.Spinbox(search_frame, from_=10, to=200, textvariable=self.num_cases_var, width=10)
        self.num_cases_spinbox.grid(row=0, column=5, sticky=tk.W, pady=5, padx=5)
        
        # Search button
        self.search_button = ttk.Button(search_frame, text="Build Case Database", command=self.build_case_database)
        self.search_button.grid(row=0, column=6, padx=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Client Information Section
        client_frame = ttk.LabelFrame(main_frame, text="Your Client's Information", padding="10")
        client_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Client criminal history
        history_frame = ttk.Frame(client_frame)
        history_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=5)
        
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
        ttk.Label(client_frame, text="Current Charge:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.case_type_var = tk.StringVar()
        self.case_type_dropdown = ttk.Combobox(client_frame, textvariable=self.case_type_var, width=25)
        self.case_type_dropdown['values'] = ['Theft', 'Grand Theft Auto', 'Burglary', 'Drug Possession', 'Drug Trafficking', 
                                            'Assault', 'Aggravated Assault', 'DUI', 'Fraud', 'Robbery', 'Armed Robbery']
        self.case_type_dropdown.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Judge selection (optional)
        ttk.Label(client_frame, text="Judge (if known):").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20,0))
        self.judge_var = tk.StringVar()
        self.judge_dropdown = ttk.Combobox(client_frame, textvariable=self.judge_var, width=25)
        self.judge_dropdown.grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # Analyze button
        self.analyze_button = ttk.Button(client_frame, text="Analyze Case Outcome", command=self.analyze_case)
        self.analyze_button.grid(row=2, column=0, columnspan=4, pady=10)
        
        # Results Section - Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Tab 1: Similar Cases
        similar_frame = ttk.Frame(self.notebook)
        self.notebook.add(similar_frame, text="Similar Cases")
        
        # Similar cases table
        self.tree_frame = ttk.Frame(similar_frame)
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
        prediction_frame = ttk.Frame(self.notebook)
        self.notebook.add(prediction_frame, text="Prediction Analysis")
        
        # Prediction results
        self.results_text = tk.Text(prediction_frame, height=20, width=80, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 3: Judge Statistics
        judge_frame = ttk.Frame(self.notebook)
        self.notebook.add(judge_frame, text="Judge Statistics")
        
        self.judge_stats_text = tk.Text(judge_frame, height=20, width=80, wrap=tk.WORD)
        self.judge_stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. API Key: " + ("Loaded ✓" if self.api_key else "Not Found ✗"))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
    def build_case_database(self):
        """Build database of criminal cases with defendant histories"""
        if not self.api_key:
            messagebox.showerror("Error", "Please set your SERPAPI_KEY in the .env file!")
            return
        
        # Run in background thread
        thread = threading.Thread(target=self._build_database_thread)
        thread.daemon = True
        thread.start()
        
    def _build_database_thread(self):
        """Background thread to build case database"""
        self.root.after(0, lambda: self.progress.configure(maximum=int(self.num_cases_var.get())))
        self.root.after(0, lambda: self.progress['value'] == 0)
        self.root.after(0, lambda: self.status_var.set("Building criminal case database..."))
        
        state = self.state_var.get()
        case_type_filter = self.search_case_type_var.get()
        num_cases = int(self.num_cases_var.get())
        
        self.case_database = []
        self.judges_data.clear()
        judges_found = set()
        
        # Search queries to find criminal cases with history
        search_queries = [
            f'"{state}" criminal "prior convictions" "sentenced to" verdict',
            f'"{state}" "criminal history" "found guilty" sentence judge',
            f'"{state}" defendant "felony record" "prison term" court',
            f'"{state}" "repeat offender" conviction sentencing criminal',
            f'"{state}" "criminal record" "plea deal" "years prison"'
        ]
        
        if case_type_filter != "All":
            search_queries = [q + f' "{case_type_filter}"' for q in search_queries]
        
        cases_found = 0
        
        try:
            for query_idx, query in enumerate(search_queries):
                if cases_found >= num_cases:
                    break
                    
                url = "https://serpapi.com/search"
                params = {
                    "engine": "google_scholar",
                    "q": query,
                    "api_key": self.api_key,
                    "num": "20",
                    "start": "0"
                }
                
                # Get multiple pages of results
                for page in range(3):  # Get 3 pages
                    if cases_found >= num_cases:
                        break
                        
                    params["start"] = str(page * 20)
                    
                    try:
                        response = requests.get(url, params=params, timeout=30)
                        if response.status_code != 200:
                            continue
                            
                        data = response.json()
                        
                        for result in data.get("organic_results", []):
                            title = result.get("title", "")
                            snippet = result.get("snippet", "")
                            text = title + " " + snippet
                            
                            # Extract case information
                            case_info = self.extract_case_details(text)
                            
                            if case_info and case_info['verdict'] != 'Unknown':
                                self.case_database.append(case_info)
                                
                                # Track judge statistics
                                if case_info['judge'] and case_info['judge'] != "Unknown":
                                    judges_found.add(case_info['judge'])
                                    self.judges_data[case_info['judge']].append(case_info)
                                
                                cases_found += 1
                                self.root.after(0, lambda v=cases_found: self.progress.configure(value=v))
                                
                                if cases_found >= num_cases:
                                    break
                                    
                    except Exception as e:
                        print(f"Error on page {page}: {e}")
                        continue
                        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to build database: {str(e)}"))
            
        # Update UI
        self.root.after(0, lambda: self.judge_dropdown.configure(values=sorted(list(judges_found))))
        self.root.after(0, lambda: self.status_var.set(f"Database built: {len(self.case_database)} cases, {len(judges_found)} judges"))
        self.root.after(0, lambda: self.progress.configure(value=0))
        
    def extract_case_details(self, text):
        """Extract detailed case information including criminal history"""
        case = {
            'defendant': 'Unknown',
            'criminal_history': self.extract_criminal_history(text),
            'charge': self.extract_case_type(text),
            'verdict': self.extract_verdict(text),
            'sentence': self.extract_punishment(text),
            'judge': self.extract_judge(text),
            'prior_felonies': 0,
            'prior_misdemeanors': 0,
            'prior_convictions': 0
        }
        
        # Extract defendant name
        defendant_patterns = [
            r'(?:defendant|Defendant)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:State\s+v\.\s+|People\s+v\.\s+|U\.S\.\s+v\.\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|pled|pleaded|found)'
        ]
        
        for pattern in defendant_patterns:
            match = re.search(pattern, text)
            if match:
                case['defendant'] = match.group(1)
                break
        
        # Parse criminal history numbers
        history_text = case['criminal_history']
        
        # Extract felonies
        felony_match = re.search(r'(\d+)\s*(?:prior\s*)?felon', history_text, re.IGNORECASE)
        if felony_match:
            case['prior_felonies'] = int(felony_match.group(1))
            
        # Extract misdemeanors
        misdem_match = re.search(r'(\d+)\s*(?:prior\s*)?misdemeanor', history_text, re.IGNORECASE)
        if misdem_match:
            case['prior_misdemeanors'] = int(misdem_match.group(1))
            
        # Extract total convictions
        conviction_match = re.search(r'(\d+)\s*(?:prior\s*)?conviction', history_text, re.IGNORECASE)
        if conviction_match:
            case['prior_convictions'] = int(conviction_match.group(1))
        else:
            case['prior_convictions'] = case['prior_felonies'] + case['prior_misdemeanors']
        
        return case
    
    def extract_criminal_history(self, text):
        """Extract criminal history information"""
        history_patterns = [
            r'(?:criminal\s+history|prior\s+record|criminal\s+record)(?:\s+of)?[:\s]+([^.;]+)',
            r'(\d+\s+(?:prior\s+)?(?:conviction|felony|felonies|misdemeanor)[^.;]*)',
            r'(?:prior\s+convictions?|previous\s+convictions?)(?:\s+for)?[:\s]+([^.;]+)',
            r'(?:repeat\s+offender|recidivist|habitual\s+criminal)[^.;]*',
            r'(?:first[\s-]time\s+offender|no\s+prior\s+record|clean\s+record)'
        ]
        
        text_lower = text.lower()
        
        # Check for first-time offender
        if any(phrase in text_lower for phrase in ['first-time offender', 'first time offender', 'no prior record', 'clean record']):
            return "No prior record"
        
        # Look for criminal history descriptions
        for pattern in history_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                history = match.group(0).strip()
                # Clean up the history text
                history = re.sub(r'\s+', ' ', history)
                return history
        
        # Look for specific numbers
        if 'repeat offender' in text_lower or 'recidivist' in text_lower:
            return "Multiple prior convictions"
        
        return "Unknown criminal history"
    
    def extract_case_type(self, text):
        """Extract case type from text"""
        case_types = {
            'murder': 'Murder',
            'homicide': 'Homicide',
            'manslaughter': 'Manslaughter',
            'assault': 'Assault',
            'aggravated assault': 'Aggravated Assault',
            'battery': 'Battery',
            'theft': 'Theft',
            'grand theft': 'Grand Theft',
            'larceny': 'Larceny',
            'burglary': 'Burglary',
            'robbery': 'Robbery',
            'armed robbery': 'Armed Robbery',
            'drug possession': 'Drug Possession',
            'drug trafficking': 'Drug Trafficking',
            'drug': 'Drug Offense',
            'narcotic': 'Drug Offense',
            'fraud': 'Fraud',
            'embezzlement': 'Embezzlement',
            'dui': 'DUI',
            'dwi': 'DUI',
            'domestic violence': 'Domestic Violence',
            'sexual assault': 'Sexual Assault',
            'rape': 'Rape',
            'arson': 'Arson',
            'vandalism': 'Vandalism',
            'weapons': 'Weapons Charge',
            'firearm': 'Weapons Charge',
            'kidnapping': 'Kidnapping',
            'conspiracy': 'Conspiracy'
        }
        
        text_lower = text.lower()
        
        # Check for exact matches first
        for keyword, case_type in sorted(case_types.items(), key=lambda x: len(x[0]), reverse=True):
            if keyword in text_lower:
                return case_type
        
        return "Criminal Offense"
    
    def extract_verdict(self, text):
        """Extract verdict from text"""
        text_lower = text.lower()
        
        if any(phrase in text_lower for phrase in ['found guilty', 'convicted of', 'guilty verdict', 'conviction for']):
            return "Guilty"
        elif any(phrase in text_lower for phrase in ['not guilty', 'acquitted', 'acquittal', 'charges dismissed']):
            return "Not Guilty"
        elif any(phrase in text_lower for phrase in ['plea deal', 'plea bargain', 'pled guilty', 'pleaded guilty', 'guilty plea']):
            return "Plea Deal"
        elif 'mistrial' in text_lower:
            return "Mistrial"
        elif any(phrase in text_lower for phrase in ['sentenced to', 'prison term', 'jail time']):
            return "Guilty"  # If sentenced, they were found guilty
        
        return "Unknown"
    
    def extract_punishment(self, text):
        """Extract punishment/sentence from text"""
        # Death penalty
        if any(phrase in text.lower() for phrase in ['death penalty', 'death sentence', 'capital punishment']):
            return "Death Penalty"
        
        # Life sentences
        if any(phrase in text.lower() for phrase in ['life in prison', 'life sentence', 'life without parole', 'lwop']):
            return "Life in Prison"
        
        # Look for specific sentences
        sentence_patterns = [
            r'sentenced?\s+to\s+(\d+)\s*(?:to\s*)?(\d+)?\s*(year|month|day)s?(?:\s+in\s+prison)?',
            r'(\d+)\s*(?:to\s*)?(\d+)?\s*(year|month|day)s?\s+(?:in\s+)?(?:state\s+)?prison',
            r'(\d+)\s*(year|month|day)s?\s+(?:prison|jail)\s*(?:sentence|term)',
            r'prison\s+term\s+of\s+(\d+)\s*(year|month)s?'
        ]
        
        for pattern in sentence_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        # Probation
        probation_match = re.search(r'(\d+)\s*(year|month)s?\s*(?:of\s*)?probation', text, re.IGNORECASE)
        if probation_match:
            return probation_match.group(0)
        
        # Fines
        fine_match = re.search(r'\$[\d,]+(?:\.\d{2})?\s*(?:fine|penalty|restitution)', text, re.IGNORECASE)
        if fine_match:
            return fine_match.group(0)
        
        # Community service
        service_match = re.search(r'(\d+)\s*hours?\s*(?:of\s*)?community\s*service', text, re.IGNORECASE)
        if service_match:
            return service_match.group(0)
        
        return "Not specified"
    
    def extract_judge(self, text):
        """Extract judge name from text"""
        judge_patterns = [
            r'Judge\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'Justice\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'Hon\.\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'Honorable\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
            r'before\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+),?\s+J\.'
        ]
        
        for pattern in judge_patterns:
            match = re.search(pattern, text)
            if match:
                return f"Judge {match.group(1)}"
        
        return "Unknown"
    
    def analyze_case(self):
        """Analyze client's case based on similar cases"""
        if not self.case_database:
            messagebox.showwarning("Warning", "Please build the case database first!")
            return
        
        if not self.case_type_var.get():
            messagebox.showwarning("Warning", "Please select the current charge!")
            return
        
        # Get client info
        client_felonies = int(self.felonies_var.get())
        client_misdemeanors = int(self.misdemeanors_var.get())
        client_convictions = int(self.convictions_var.get())
        client_charge = self.case_type_var.get()
        selected_judge = self.judge_var.get()
        
        # Find similar cases
        self.similar_cases = []
        
        for case in self.case_database:
            similarity_score = 0
            
            # Match charge type
            if client_charge.lower() in case['charge'].lower() or case['charge'].lower() in client_charge.lower():
                similarity_score += 5
            
            # Match criminal history
            if abs(case['prior_felonies'] - client_felonies) <= 1:
                similarity_score += 3
            if abs(case['prior_misdemeanors'] - client_misdemeanors) <= 2:
                similarity_score += 2
            if abs(case['prior_convictions'] - client_convictions) <= 2:
                similarity_score += 2
                
            # Match judge if specified
            if selected_judge and case['judge'] == selected_judge:
                similarity_score += 4
            
            if similarity_score > 0:
                self.similar_cases.append((similarity_score, case))
        
        # Sort by similarity
        self.similar_cases.sort(key=lambda x: x[0], reverse=True)
        self.similar_cases = [case for _, case in self.similar_cases[:50]]  # Top 50 similar cases
        
        # Display results
        self.display_similar_cases()
        self.generate_prediction()
        self.generate_judge_stats()
        
    def display_similar_cases(self):
        """Display similar cases in the table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add similar cases
        for case in self.similar_cases[:20]:  # Show top 20
            self.tree.insert('', 'end', values=(
                case['defendant'],
                case['criminal_history'],
                case['charge'],
                case['verdict'],
                case['sentence'],
                case['judge']
            ))
    
    def generate_prediction(self):
        """Generate prediction based on similar cases"""
        self.results_text.delete(1.0, tk.END)
        
        if not self.similar_cases:
            self.results_text.insert(tk.END, "No similar cases found in the database.\n")
            return
        
        # Calculate statistics
        total_cases = len(self.similar_cases)
        guilty_count = sum(1 for case in self.similar_cases if case['verdict'] == 'Guilty')
        not_guilty_count = sum(1 for case in self.similar_cases if case['verdict'] == 'Not Guilty')
        plea_count = sum(1 for case in self.similar_cases if case['verdict'] == 'Plea Deal')
        
        guilty_rate = (guilty_count / total_cases) * 100 if total_cases > 0 else 0
        not_guilty_rate = (not_guilty_count / total_cases) * 100 if total_cases > 0 else 0
        plea_rate = (plea_count / total_cases) * 100 if total_cases > 0 else 0
        
        # Analyze sentences for guilty verdicts
        sentences = []
        for case in self.similar_cases:
            if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                # Extract years from sentence
                years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                if years_match:
                    sentences.append(int(years_match.group(1)))
        
        # Generate report
        report = f"CASE OUTCOME PREDICTION REPORT\n"
        report += f"{'='*60}\n\n"
        
        report += f"Client Profile:\n"
        report += f"- Current Charge: {self.case_type_var.get()}\n"
        report += f"- Prior Felonies: {self.felonies_var.get()}\n"
        report += f"- Prior Misdemeanors: {self.misdemeanors_var.get()}\n"
        report += f"- Total Prior Convictions: {self.convictions_var.get()}\n"
        if self.judge_var.get():
            report += f"- Assigned Judge: {self.judge_var.get()}\n"
        report += f"\n"
        
        report += f"Analysis Based on {total_cases} Similar Cases:\n"
        report += f"{'='*60}\n\n"
        
        report += f"VERDICT PROBABILITIES:\n"
        report += f"- Guilty: {guilty_rate:.1f}% ({guilty_count} cases)\n"
        report += f"- Not Guilty: {not_guilty_rate:.1f}% ({not_guilty_count} cases)\n"
        report += f"- Plea Deal: {plea_rate:.1f}% ({plea_count} cases)\n\n"



    
    def generate_judge_stats(self):
            """Generate statistics for all judges in database"""
            self.judge_stats_text.delete(1.0, tk.END)
            
            if not self.judges_data:
                self.judge_stats_text.insert(tk.END, "No judge data available.\n")
                return
            
            stats = f"JUDGE STATISTICS REPORT\n"
            stats += f"{'='*60}\n\n"
            
            # Sort judges by number of cases
            sorted_judges = sorted(self.judges_data.items(), key=lambda x: len(x[1]), reverse=True)
            
            for judge, cases in sorted_judges[:20]:  # Top 20 judges
                total = len(cases)
                guilty = sum(1 for case in cases if case['verdict'] == 'Guilty')
                not_guilty = sum(1 for case in cases if case['verdict'] == 'Not Guilty')
                plea_deals = sum(1 for case in cases if case['verdict'] == 'Plea Deal')
                
                guilty_rate = (guilty / total * 100) if total > 0 else 0
                
                stats += f"{judge}\n"
                stats += f"- Total Cases: {total}\n"
                stats += f"- Conviction Rate: {guilty_rate:.1f}%\n"
                stats += f"- Guilty: {guilty}, Not Guilty: {not_guilty}, Plea Deals: {plea_deals}\n"
                
                # Average sentence length
                sentences = []
                for case in cases:
                    if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                        years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                        if years_match:
                            sentences.append(int(years_match.group(1)))
                
                if sentences:
                    avg_sentence = sum(sentences) / len(sentences)
                    stats += f"- Average Sentence: {avg_sentence:.1f} years\n"
                
                stats += f"{'-'*40}\n\n"
            
            self.judge_stats_text.insert(tk.END, stats)
    
    def main():
        root = tk.Tk()
        app = JudicialAnalyzer(root)
        root.mainloop()
    
    if __name__ == "__main__":
        main()import tkinter as tk
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
    from collections import defaultdict
    
    # Load environment variables
    load_dotenv()
    
    class JudicialAnalyzer:
        def __init__(self, root):
            self.root = root
            self.root.title("Criminal Case Outcome Predictor")
            self.root.geometry("1200x800")
            
            # Data storage
            self.case_database = []  # All cases found
            self.similar_cases = []  # Cases similar to client
            self.judges_data = defaultdict(list)  # Judge -> cases mapping
            
            # API Key
            self.api_key = os.getenv('SERPAPI_KEY', '')
            print(f"API Key loaded: {'Yes' if self.api_key else 'No'}")
            
            self.setup_ui()
            
        def setup_ui(self):
            # Main container
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Search Section
            search_frame = ttk.LabelFrame(main_frame, text="Search Criminal Cases Database", padding="10")
            search_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
            
            # State selection
            ttk.Label(search_frame, text="State:").grid(row=0, column=0, sticky=tk.W, pady=5)
            self.state_var = tk.StringVar(value="California")
            self.state_dropdown = ttk.Combobox(search_frame, textvariable=self.state_var, width=20)
            self.state_dropdown['values'] = ['California', 'New York', 'Texas', 'Florida', 'Illinois']
            self.state_dropdown.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)
            
            # Case type filter
            ttk.Label(search_frame, text="Case Type:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20,0))
            self.search_case_type_var = tk.StringVar(value="All")
            self.search_case_type_dropdown = ttk.Combobox(search_frame, textvariable=self.search_case_type_var, width=20)
            self.search_case_type_dropdown['values'] = ['All', 'Theft', 'Drug Offense', 'Assault', 'DUI', 'Fraud', 'Burglary', 'Robbery', 'Murder']
            self.search_case_type_dropdown.grid(row=0, column=3, sticky=tk.W, pady=5, padx=5)
            
            # Number of cases to fetch
            ttk.Label(search_frame, text="Cases to Analyze:").grid(row=0, column=4, sticky=tk.W, pady=5, padx=(20,0))
            self.num_cases_var = tk.StringVar(value="50")
            self.num_cases_spinbox = ttk.Spinbox(search_frame, from_=10, to=200, textvariable=self.num_cases_var, width=10)
            self.num_cases_spinbox.grid(row=0, column=5, sticky=tk.W, pady=5, padx=5)
            
            # Search button
            self.search_button = ttk.Button(search_frame, text="Build Case Database", command=self.build_case_database)
            self.search_button.grid(row=0, column=6, padx=20)
            
            # Progress bar
            self.progress = ttk.Progressbar(main_frame, mode='determinate')
            self.progress.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
            
            # Client Information Section
            client_frame = ttk.LabelFrame(main_frame, text="Your Client's Information", padding="10")
            client_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
            
            # Client criminal history
            history_frame = ttk.Frame(client_frame)
            history_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=5)
            
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
            ttk.Label(client_frame, text="Current Charge:").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.case_type_var = tk.StringVar()
            self.case_type_dropdown = ttk.Combobox(client_frame, textvariable=self.case_type_var, width=25)
            self.case_type_dropdown['values'] = ['Theft', 'Grand Theft Auto', 'Burglary', 'Drug Possession', 'Drug Trafficking', 
                                                'Assault', 'Aggravated Assault', 'DUI', 'Fraud', 'Robbery', 'Armed Robbery']
            self.case_type_dropdown.grid(row=1, column=1, sticky=tk.W, pady=5)
            
            # Judge selection (optional)
            ttk.Label(client_frame, text="Judge (if known):").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20,0))
            self.judge_var = tk.StringVar()
            self.judge_dropdown = ttk.Combobox(client_frame, textvariable=self.judge_var, width=25)
            self.judge_dropdown.grid(row=1, column=3, sticky=tk.W, pady=5)
            
            # Analyze button
            self.analyze_button = ttk.Button(client_frame, text="Analyze Case Outcome", command=self.analyze_case)
            self.analyze_button.grid(row=2, column=0, columnspan=4, pady=10)
            
            # Results Section - Notebook for tabs
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
            
            # Tab 1: Similar Cases
            similar_frame = ttk.Frame(self.notebook)
            self.notebook.add(similar_frame, text="Similar Cases")
            
            # Similar cases table
            self.tree_frame = ttk.Frame(similar_frame)
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
            prediction_frame = ttk.Frame(self.notebook)
            self.notebook.add(prediction_frame, text="Prediction Analysis")
            
            # Prediction results
            self.results_text = tk.Text(prediction_frame, height=20, width=80, wrap=tk.WORD)
            self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Tab 3: Judge Statistics
            judge_frame = ttk.Frame(self.notebook)
            self.notebook.add(judge_frame, text="Judge Statistics")
            
            self.judge_stats_text = tk.Text(judge_frame, height=20, width=80, wrap=tk.WORD)
            self.judge_stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Status bar
            self.status_var = tk.StringVar()
            self.status_var.set("Ready. API Key: " + ("Loaded ✓" if self.api_key else "Not Found ✗"))
            status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
            status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
            
            # Configure grid weights
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(3, weight=1)
            
        def build_case_database(self):
            """Build database of criminal cases with defendant histories"""
            if not self.api_key:
                messagebox.showerror("Error", "Please set your SERPAPI_KEY in the .env file!")
                return
            
            # Run in background thread
            thread = threading.Thread(target=self._build_database_thread)
            thread.daemon = True
            thread.start()
            
        def _build_database_thread(self):
            """Background thread to build case database"""
            self.root.after(0, lambda: self.progress.configure(maximum=int(self.num_cases_var.get())))
            self.root.after(0, lambda: self.progress['value'] == 0)
            self.root.after(0, lambda: self.status_var.set("Building criminal case database..."))
            
            state = self.state_var.get()
            case_type_filter = self.search_case_type_var.get()
            num_cases = int(self.num_cases_var.get())
            
            self.case_database = []
            self.judges_data.clear()
            judges_found = set()
            
            # Search queries to find criminal cases with history
            search_queries = [
                f'"{state}" criminal "prior convictions" "sentenced to" verdict',
                f'"{state}" "criminal history" "found guilty" sentence judge',
                f'"{state}" defendant "felony record" "prison term" court',
                f'"{state}" "repeat offender" conviction sentencing criminal',
                f'"{state}" "criminal record" "plea deal" "years prison"'
            ]
            
            if case_type_filter != "All":
                search_queries = [q + f' "{case_type_filter}"' for q in search_queries]
            
            cases_found = 0
            
            try:
                for query_idx, query in enumerate(search_queries):
                    if cases_found >= num_cases:
                        break
                        
                    url = "https://serpapi.com/search"
                    params = {
                        "engine": "google_scholar",
                        "q": query,
                        "api_key": self.api_key,
                        "num": "20",
                        "start": "0"
                    }
                    
                    # Get multiple pages of results
                    for page in range(3):  # Get 3 pages
                        if cases_found >= num_cases:
                            break
                            
                        params["start"] = str(page * 20)
                        
                        try:
                            response = requests.get(url, params=params, timeout=30)
                            if response.status_code != 200:
                                continue
                                
                            data = response.json()
                            
                            for result in data.get("organic_results", []):
                                title = result.get("title", "")
                                snippet = result.get("snippet", "")
                                text = title + " " + snippet
                                
                                # Extract case information
                                case_info = self.extract_case_details(text)
                                
                                if case_info and case_info['verdict'] != 'Unknown':
                                    self.case_database.append(case_info)
                                    
                                    # Track judge statistics
                                    if case_info['judge'] and case_info['judge'] != "Unknown":
                                        judges_found.add(case_info['judge'])
                                        self.judges_data[case_info['judge']].append(case_info)
                                    
                                    cases_found += 1
                                    self.root.after(0, lambda v=cases_found: self.progress.configure(value=v))
                                    
                                    if cases_found >= num_cases:
                                        break
                                        
                        except Exception as e:
                            print(f"Error on page {page}: {e}")
                            continue
                            
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to build database: {str(e)}"))
                
            # Update UI
            self.root.after(0, lambda: self.judge_dropdown.configure(values=sorted(list(judges_found))))
            self.root.after(0, lambda: self.status_var.set(f"Database built: {len(self.case_database)} cases, {len(judges_found)} judges"))
            self.root.after(0, lambda: self.progress.configure(value=0))
            
        def extract_case_details(self, text):
            """Extract detailed case information including criminal history"""
            case = {
                'defendant': 'Unknown',
                'criminal_history': self.extract_criminal_history(text),
                'charge': self.extract_case_type(text),
                'verdict': self.extract_verdict(text),
                'sentence': self.extract_punishment(text),
                'judge': self.extract_judge(text),
                'prior_felonies': 0,
                'prior_misdemeanors': 0,
                'prior_convictions': 0
            }
            
            # Extract defendant name
            defendant_patterns = [
                r'(?:defendant|Defendant)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'(?:State\s+v\.\s+|People\s+v\.\s+|U\.S\.\s+v\.\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:was|pled|pleaded|found)'
            ]
            
            for pattern in defendant_patterns:
                match = re.search(pattern, text)
                if match:
                    case['defendant'] = match.group(1)
                    break
            
            # Parse criminal history numbers
            history_text = case['criminal_history']
            
            # Extract felonies
            felony_match = re.search(r'(\d+)\s*(?:prior\s*)?felon', history_text, re.IGNORECASE)
            if felony_match:
                case['prior_felonies'] = int(felony_match.group(1))
                
            # Extract misdemeanors
            misdem_match = re.search(r'(\d+)\s*(?:prior\s*)?misdemeanor', history_text, re.IGNORECASE)
            if misdem_match:
                case['prior_misdemeanors'] = int(misdem_match.group(1))
                
            # Extract total convictions
            conviction_match = re.search(r'(\d+)\s*(?:prior\s*)?conviction', history_text, re.IGNORECASE)
            if conviction_match:
                case['prior_convictions'] = int(conviction_match.group(1))
            else:
                case['prior_convictions'] = case['prior_felonies'] + case['prior_misdemeanors']
            
            return case
        
        def extract_criminal_history(self, text):
            """Extract criminal history information"""
            history_patterns = [
                r'(?:criminal\s+history|prior\s+record|criminal\s+record)(?:\s+of)?[:\s]+([^.;]+)',
                r'(\d+\s+(?:prior\s+)?(?:conviction|felony|felonies|misdemeanor)[^.;]*)',
                r'(?:prior\s+convictions?|previous\s+convictions?)(?:\s+for)?[:\s]+([^.;]+)',
                r'(?:repeat\s+offender|recidivist|habitual\s+criminal)[^.;]*',
                r'(?:first[\s-]time\s+offender|no\s+prior\s+record|clean\s+record)'
            ]
            
            text_lower = text.lower()
            
            # Check for first-time offender
            if any(phrase in text_lower for phrase in ['first-time offender', 'first time offender', 'no prior record', 'clean record']):
                return "No prior record"
            
            # Look for criminal history descriptions
            for pattern in history_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    history = match.group(0).strip()
                    # Clean up the history text
                    history = re.sub(r'\s+', ' ', history)
                    return history
            
            # Look for specific numbers
            if 'repeat offender' in text_lower or 'recidivist' in text_lower:
                return "Multiple prior convictions"
            
            return "Unknown criminal history"
        
        def extract_case_type(self, text):
            """Extract case type from text"""
            case_types = {
                'murder': 'Murder',
                'homicide': 'Homicide',
                'manslaughter': 'Manslaughter',
                'assault': 'Assault',
                'aggravated assault': 'Aggravated Assault',
                'battery': 'Battery',
                'theft': 'Theft',
                'grand theft': 'Grand Theft',
                'larceny': 'Larceny',
                'burglary': 'Burglary',
                'robbery': 'Robbery',
                'armed robbery': 'Armed Robbery',
                'drug possession': 'Drug Possession',
                'drug trafficking': 'Drug Trafficking',
                'drug': 'Drug Offense',
                'narcotic': 'Drug Offense',
                'fraud': 'Fraud',
                'embezzlement': 'Embezzlement',
                'dui': 'DUI',
                'dwi': 'DUI',
                'domestic violence': 'Domestic Violence',
                'sexual assault': 'Sexual Assault',
                'rape': 'Rape',
                'arson': 'Arson',
                'vandalism': 'Vandalism',
                'weapons': 'Weapons Charge',
                'firearm': 'Weapons Charge',
                'kidnapping': 'Kidnapping',
                'conspiracy': 'Conspiracy'
            }
            
            text_lower = text.lower()
            
            # Check for exact matches first
            for keyword, case_type in sorted(case_types.items(), key=lambda x: len(x[0]), reverse=True):
                if keyword in text_lower:
                    return case_type
            
            return "Criminal Offense"
        
        def extract_verdict(self, text):
            """Extract verdict from text"""
            text_lower = text.lower()
            
            if any(phrase in text_lower for phrase in ['found guilty', 'convicted of', 'guilty verdict', 'conviction for']):
                return "Guilty"
            elif any(phrase in text_lower for phrase in ['not guilty', 'acquitted', 'acquittal', 'charges dismissed']):
                return "Not Guilty"
            elif any(phrase in text_lower for phrase in ['plea deal', 'plea bargain', 'pled guilty', 'pleaded guilty', 'guilty plea']):
                return "Plea Deal"
            elif 'mistrial' in text_lower:
                return "Mistrial"
            elif any(phrase in text_lower for phrase in ['sentenced to', 'prison term', 'jail time']):
                return "Guilty"  # If sentenced, they were found guilty
            
            return "Unknown"
        
        def extract_punishment(self, text):
            """Extract punishment/sentence from text"""
            # Death penalty
            if any(phrase in text.lower() for phrase in ['death penalty', 'death sentence', 'capital punishment']):
                return "Death Penalty"
            
            # Life sentences
            if any(phrase in text.lower() for phrase in ['life in prison', 'life sentence', 'life without parole', 'lwop']):
                return "Life in Prison"
            
            # Look for specific sentences
            sentence_patterns = [
                r'sentenced?\s+to\s+(\d+)\s*(?:to\s*)?(\d+)?\s*(year|month|day)s?(?:\s+in\s+prison)?',
                r'(\d+)\s*(?:to\s*)?(\d+)?\s*(year|month|day)s?\s+(?:in\s+)?(?:state\s+)?prison',
                r'(\d+)\s*(year|month|day)s?\s+(?:prison|jail)\s*(?:sentence|term)',
                r'prison\s+term\s+of\s+(\d+)\s*(year|month)s?'
            ]
            
            for pattern in sentence_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(0).strip()
            
            # Probation
            probation_match = re.search(r'(\d+)\s*(year|month)s?\s*(?:of\s*)?probation', text, re.IGNORECASE)
            if probation_match:
                return probation_match.group(0)
            
            # Fines
            fine_match = re.search(r'\$[\d,]+(?:\.\d{2})?\s*(?:fine|penalty|restitution)', text, re.IGNORECASE)
            if fine_match:
                return fine_match.group(0)
            
            # Community service
            service_match = re.search(r'(\d+)\s*hours?\s*(?:of\s*)?community\s*service', text, re.IGNORECASE)
            if service_match:
                return service_match.group(0)
            
            return "Not specified"
        
        def extract_judge(self, text):
            """Extract judge name from text"""
            judge_patterns = [
                r'Judge\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                r'Justice\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                r'Hon\.\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                r'Honorable\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                r'before\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+),?\s+J\.'
            ]
            
            for pattern in judge_patterns:
                match = re.search(pattern, text)
                if match:
                    return f"Judge {match.group(1)}"
            
            return "Unknown"
        
        def analyze_case(self):
            """Analyze client's case based on similar cases"""
            if not self.case_database:
                messagebox.showwarning("Warning", "Please build the case database first!")
                return
            
            if not self.case_type_var.get():
                messagebox.showwarning("Warning", "Please select the current charge!")
                return
            
            # Get client info
            client_felonies = int(self.felonies_var.get())
            client_misdemeanors = int(self.misdemeanors_var.get())
            client_convictions = int(self.convictions_var.get())
            client_charge = self.case_type_var.get()
            selected_judge = self.judge_var.get()
            
            # Find similar cases
            self.similar_cases = []
            
            for case in self.case_database:
                similarity_score = 0
                
                # Match charge type
                if client_charge.lower() in case['charge'].lower() or case['charge'].lower() in client_charge.lower():
                    similarity_score += 5
                
                # Match criminal history
                if abs(case['prior_felonies'] - client_felonies) <= 1:
                    similarity_score += 3
                if abs(case['prior_misdemeanors'] - client_misdemeanors) <= 2:
                    similarity_score += 2
                if abs(case['prior_convictions'] - client_convictions) <= 2:
                    similarity_score += 2
                    
                # Match judge if specified
                if selected_judge and case['judge'] == selected_judge:
                    similarity_score += 4
                
                if similarity_score > 0:
                    self.similar_cases.append((similarity_score, case))
            
            # Sort by similarity
            self.similar_cases.sort(key=lambda x: x[0], reverse=True)
            self.similar_cases = [case for _, case in self.similar_cases[:50]]  # Top 50 similar cases
            
            # Display results
            self.display_similar_cases()
            self.generate_prediction()
            self.generate_judge_stats()
            
        def display_similar_cases(self):
            """Display similar cases in the table"""
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add similar cases
            for case in self.similar_cases[:20]:  # Show top 20
                self.tree.insert('', 'end', values=(
                    case['defendant'],
                    case['criminal_history'],
                    case['charge'],
                    case['verdict'],
                    case['sentence'],
                    case['judge']
                ))
        
        def generate_prediction(self):
            """Generate prediction based on similar cases"""
            self.results_text.delete(1.0, tk.END)
            
            if not self.similar_cases:
                self.results_text.insert(tk.END, "No similar cases found in the database.\n")
                return
            
            # Calculate statistics
            total_cases = len(self.similar_cases)
            guilty_count = sum(1 for case in self.similar_cases if case['verdict'] == 'Guilty')
            not_guilty_count = sum(1 for case in self.similar_cases if case['verdict'] == 'Not Guilty')
            plea_count = sum(1 for case in self.similar_cases if case['verdict'] == 'Plea Deal')
            
            guilty_rate = (guilty_count / total_cases) * 100 if total_cases > 0 else 0
            not_guilty_rate = (not_guilty_count / total_cases) * 100 if total_cases > 0 else 0
            plea_rate = (plea_count / total_cases) * 100 if total_cases > 0 else 0
            
            # Analyze sentences for guilty verdicts
            sentences = []
            for case in self.similar_cases:
                if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                    # Extract years from sentence
                    years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                    if years_match:
                        sentences.append(int(years_match.group(1)))
            
            # Generate report
            report = f"CASE OUTCOME PREDICTION REPORT\n"
            report += f"{'='*60}\n\n"
            
            report += f"Client Profile:\n"
            report += f"- Current Charge: {self.case_type_var.get()}\n"
            report += f"- Prior Felonies: {self.felonies_var.get()}\n"
            report += f"- Prior Misdemeanors: {self.misdemeanors_var.get()}\n"
            report += f"- Total Prior Convictions: {self.convictions_var.get()}\n"
            if self.judge_var.get():
                report += f"- Assigned Judge: {self.judge_var.get()}\n"
            report += f"\n"
            
            report += f"Analysis Based on {total_cases} Similar Cases:\n"
            report += f"{'='*60}\n\n"
            
            report += f"VERDICT PROBABILITIES:\n"
            report += f"- Guilty: {guilty_rate:.1f}% ({guilty_count} cases)\n"
            report += f"- Not Guilty: {not_guilty_rate:.1f}% ({not_guilty_count} cases)\n"
            report += f"- Plea Deal: {plea_rate:.1f}% ({plea_count} cases)\n\n"
            
            if sentences:
                avg_sentence = sum(sentences) / len(sentences)
                min_sentence = min(sentences)
                max_sentence = max(sentences)
                
                report += f"SENTENCING ANALYSIS (for guilty verdicts):\n"
                report += f"- Average Sentence: {avg_sentence:.1f} years\n"
                report += f"- Minimum Sentence: {min_sentence} years\n"
                report += f"- Maximum Sentence: {max_sentence} years\n"
                report += f"- Based on {len(sentences)} cases with prison sentences\n\n"
            
            # Risk assessment
            report += f"RISK ASSESSMENT:\n"
            if guilty_rate > 75:
                report += f"⚠️ HIGH RISK: {guilty_rate:.1f}% conviction rate in similar cases\n"
                report += f"   Strong recommendation to consider plea negotiations\n"
            elif guilty_rate > 50:
                report += f"⚡ MODERATE RISK: {guilty_rate:.1f}% conviction rate in similar cases\n"
                report += f"   Consider both trial and plea options carefully\n"
            else:
                report += f"✅ LOWER RISK: {guilty_rate:.1f}% conviction rate in similar cases\n"
                report += f"   Trial may be a viable option\n"
            
            # Criminal history impact
            report += f"\nCRIMINAL HISTORY IMPACT:\n"
            
            # Compare outcomes for similar criminal histories
            similar_history_cases = [case for case in self.similar_cases 
                                   if abs(case['prior_felonies'] - int(self.felonies_var.get())) <= 1]
            
            if similar_history_cases:
                similar_guilty = sum(1 for case in similar_history_cases if case['verdict'] == 'Guilty')
                similar_rate = (similar_guilty / len(similar_history_cases)) * 100
                report += f"- Defendants with similar criminal history: {similar_rate:.1f}% conviction rate\n"
                
                # Compare sentences based on criminal history
                history_sentences = []
                for case in similar_history_cases:
                    if case['verdict'] == 'Guilty' and case['sentence'] != 'Not specified':
                        years_match = re.search(r'(\d+)\s*year', case['sentence'], re.IGNORECASE)
                        if years_match:
                            history_sentences.append(int(years_match.group(1)))
                
                if history_sentences:
                    avg_history_sentence = sum(history_sentences) / len(history_sentences)
                    report += f"- Average sentence for similar criminal history: {avg_history_sentence:.1f} years\n"
            
            # Judge-specific analysis if selected
            if self.judge_var.get():
                judge_cases = [case for case in self.similar_cases if case['judge'] == self.judge_var.get()]
                if judge_cases:
                    judge_guilty = sum(1 for case in judge_cases if case['verdict'] == 'Guilty')
                    judge_rate = (judge_guilty / len(judge_cases)) * 100
                    report += f"\nJUDGE-SPECIFIC ANALYSIS ({self.judge_var.get()}):\n"
                    report += f"- Conviction rate for similar cases: {judge_rate:.1f}%\n"
                    report += f"- Based on {len(judge_cases)} similar cases before this judge\n"
            
            report += f"\nRECOMMENDATIONS:\n"
            report += f"{'='*60}\n"
            
            if guilty_rate > 70:
                report += "1. Strongly consider plea negotiations\n"
                report += "2. Focus on mitigation factors and sentencing alternatives\n"
                report += "3. Prepare comprehensive character references\n"
            elif guilty_rate > 50:
                report += "1. Evaluate strength of prosecution's evidence carefully\n"
                report += "2. Consider both plea and trial options\n"
                report += "3. Focus on reasonable doubt arguments\n"
            else:
                report += "1. Trial appears to be a viable option\n"
                report += "2. Focus on weaknesses in prosecution's case\n"
                report += "3. Consider aggressive defense strategy\n"
            
            if int(self.felonies_var.get()) > 0:
                report += "4. Address criminal history directly - focus on rehabilitation\n"
            
            report += f"\nDISCLAIMER: This analysis is based on {total_cases} similar cases found in\n"
            report += "Google Scholar. Actual outcomes may vary. Always consult with your attorney\n"
            report += "for legal advice specific to your case.\n"
            
            self.results_text.insert(tk.END, report)
