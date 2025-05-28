"""
Configuration constants for Criminal Case Outcome Predictor
"""

# States available for search
STATES = ['California', 'New York', 'Texas', 'Florida', 'Illinois']

# Case types for filtering
CASE_TYPES = ['All', 'Theft', 'Drug Offense', 'Assault', 'DUI', 'Fraud', 'Burglary', 'Robbery', 'Murder']

# Charge types for client
CHARGE_TYPES = [
    'Theft', 
    'Grand Theft Auto', 
    'Burglary', 
    'Drug Possession', 
    'Drug Trafficking',
    'Assault', 
    'Aggravated Assault', 
    'DUI', 
    'Fraud', 
    'Robbery', 
    'Armed Robbery'
]

# Search queries for finding criminal cases
SEARCH_QUERIES = [
    '"{state}" criminal "prior convictions" "sentenced to" verdict',
    '"{state}" "criminal history" "found guilty" sentence judge',
    '"{state}" defendant "felony record" "prison term" court',
    '"{state}" "repeat offender" conviction sentencing criminal',
    '"{state}" "criminal record" "plea deal" "years prison"'
]

# GUI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
MAX_SIMILAR_CASES_DISPLAY = 20
MAX_JUDGES_DISPLAY = 20

# Database Building Settings
DEFAULT_NUM_CASES = 50
MIN_CASES = 10
MAX_CASES = 200
RESULTS_PER_PAGE = 20
PAGES_PER_QUERY = 3

# Analysis Settings
SIMILARITY_WEIGHTS = {
    'charge_match': 5,
    'felony_match': 3,
    'misdemeanor_match': 2,
    'conviction_match': 2,
    'judge_match': 4
}

# Risk Assessment Thresholds
HIGH_RISK_THRESHOLD = 75  # % conviction rate
MODERATE_RISK_THRESHOLD = 50  # % conviction rate"""
Configuration constants for Criminal Case Outcome Predictor
"""

# States available for search
STATES = ['California', 'New York', 'Texas', 'Florida', 'Illinois']

# Case types for filtering
CASE_TYPES = ['All', 'Theft', 'Drug Offense', 'Assault', 'DUI', 'Fraud', 'Burglary', 'Robbery', 'Murder']

# Charge types for client
CHARGE_TYPES = [
    'Theft', 
    'Grand Theft Auto', 
    'Burglary', 
    'Drug Possession', 
    'Drug Trafficking',
    'Assault', 
    'Aggravated Assault', 
    'DUI', 
    'Fraud', 
    'Robbery', 
    'Armed Robbery'
]

# Search queries for finding criminal cases
SEARCH_QUERIES = [
    '"{state}" criminal "prior convictions" "sentenced to" verdict',
    '"{state}" "criminal history" "found guilty" sentence judge',
    '"{state}" defendant "felony record" "prison term" court',
    '"{state}" "repeat offender" conviction sentencing criminal',
    '"{state}" "criminal record" "plea deal" "years prison"'
]

# GUI Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
MAX_SIMILAR_CASES_DISPLAY = 20
MAX_JUDGES_DISPLAY = 20

# Database Building Settings
DEFAULT_NUM_CASES = 50
MIN_CASES = 10
MAX_CASES = 200
RESULTS_PER_PAGE = 20
PAGES_PER_QUERY = 3

# Analysis Settings
SIMILARITY_WEIGHTS = {
    'charge_match': 5,
    'felony_match': 3,
    'misdemeanor_match': 2,
    'conviction_match': 2,
    'judge_match': 4
}

# Risk Assessment Thresholds
HIGH_RISK_THRESHOLD = 75  # % conviction rate
MODERATE_RISK_THRESHOLD = 50  # % conviction rate
