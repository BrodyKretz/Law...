"""
Case information extraction functions for parsing Google Scholar results
"""
import re

class CaseExtractor:
    """Handles extraction of case details from text"""
    
    @staticmethod
    def extract_case_details(text):
        """Extract detailed case information including criminal history"""
        case = {
            'defendant': 'Unknown',
            'criminal_history': CaseExtractor.extract_criminal_history(text),
            'charge': CaseExtractor.extract_case_type(text),
            'verdict': CaseExtractor.extract_verdict(text),
            'sentence': CaseExtractor.extract_punishment(text),
            'judge': CaseExtractor.extract_judge(text),
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
    
    @staticmethod
    def extract_criminal_history(text):
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
    
    @staticmethod
    def extract_case_type(text):
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
    
    @staticmethod
    def extract_verdict(text):
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
    
    @staticmethod
    def extract_punishment(text):
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
    
    @staticmethod
    def extract_judge(text):
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
