"""
Database builder for fetching and storing criminal case data from Google Scholar
"""
import requests
import os
import re
from dotenv import load_dotenv
from extractors import CaseExtractor
import config

# Load environment variables
load_dotenv()

class DatabaseBuilder:
    """Handles building the case database from Google Scholar"""
    
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY', '')
        self.extractor = CaseExtractor()
    
    def search_judges_in_state(self, state):
        """
        Search for judges in a specific state using web search
        
        Args:
            state: State to search in
            
        Returns:
            list: List of judge names found
        """
        judges = set()
        
        # Search for list of judges
        search_query = f"list of {state} judges criminal court"
        
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",  # Use regular Google search for lists
            "q": search_query,
            "api_key": self.api_key,
            "num": "10"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                
                # Extract from organic results
                for result in data.get("organic_results", []):
                    snippet = result.get("snippet", "")
                    # Extract judge names from snippets
                    judge_patterns = [
                        r'Judge\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                        r'Hon\.\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                    ]
                    
                    for pattern in judge_patterns:
                        matches = re.findall(pattern, snippet)
                        for match in matches:
                            if match and len(match.split()) >= 2:
                                judges.add(f"Judge {match}")
        except:
            pass
        
        # Also search Google Scholar for criminal cases
        scholar_queries = [
            f'{state} criminal case judge verdict',
            f'{state} superior court judge criminal'
        ]
        
        for query in scholar_queries:
            results = self._search_google_scholar(query, 0)
            
            if not results:
                continue
            
            for result in results[:10]:  # Limit to first 10 results
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                text = title + " " + snippet
                
                # Extract judge names
                judge_patterns = [
                    r'Judge\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
                    r'before\s+(?:Judge\s+)?([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+),?\s+J\.',
                ]
                
                for pattern in judge_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        if match and len(match.split()) >= 2:
                            judges.add(f"Judge {match}")
        
        # Always add the option to search all cases
        judges_list = sorted(list(judges))
        if not judges_list:
            judges_list = ["Search All Criminal Cases"]
        else:
            judges_list.append("Search All Criminal Cases")
        
        return judges_list
    
    def build_judge_database(self, state, judge_name, num_cases, progress_callback=None):
        """
        Build database of cases for a specific judge
        
        Args:
            state: State to search in
            judge_name: Name of the judge
            num_cases: Number of cases to fetch
            progress_callback: Function to call with progress updates
            
        Returns:
            list: Case database for this judge
        """
        case_database = []
        
        # If "All Criminal Cases" is selected, search broadly
        if judge_name == "All Criminal Cases":
            search_queries = [
                f'{state} criminal verdict sentence defendant',
                f'{state} criminal case guilty prison term',
                f'{state} criminal defendant prior convictions'
            ]
        else:
            # Build search queries specific to this judge
            judge_simple = judge_name.replace("Judge ", "")
            search_queries = [
                f'{judge_simple} {state} criminal verdict',
                f'{judge_simple} criminal defendant sentence',
                f'{judge_simple} criminal case ruling'
            ]
        
        cases_found = 0
        
        for query_idx, query in enumerate(search_queries):
            if cases_found >= num_cases:
                break
                
            # Get multiple pages of results
            for page in range(config.PAGES_PER_QUERY):
                if cases_found >= num_cases:
                    break
                    
                results = self._search_google_scholar(query, page)
                
                if not results:
                    continue
                
                for result in results:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    text = title + " " + snippet
                    
                    # Extract case information
                    case_info = self.extractor.extract_case_details(text)
                    
                    # Set the judge name if not "All Criminal Cases"
                    if judge_name != "All Criminal Cases":
                        case_info['judge'] = judge_name
                    
                    if case_info and case_info['verdict'] != 'Unknown':
                        case_database.append(case_info)
                        cases_found += 1
                        
                        if progress_callback:
                            progress_callback(cases_found)
                        
                        if cases_found >= num_cases:
                            break
        
        return case_database
        
    def build_database(self, state, case_type_filter, num_cases, progress_callback=None):
        """
        Build database of criminal cases with defendant histories
        
        Args:
            state: State to search in
            case_type_filter: Type of cases to filter (or "All")
            num_cases: Number of cases to fetch
            progress_callback: Function to call with progress updates
            
        Returns:
            tuple: (case_database, judges_data)
        """
        case_database = []
        judges_data = {}
        
        # Build search queries
        search_queries = [query.format(state=state) for query in config.SEARCH_QUERIES]
        
        if case_type_filter != "All":
            search_queries = [q + f' "{case_type_filter}"' for q in search_queries]
        
        cases_found = 0
        
        for query_idx, query in enumerate(search_queries):
            if cases_found >= num_cases:
                break
                
            # Get multiple pages of results
            for page in range(config.PAGES_PER_QUERY):
                if cases_found >= num_cases:
                    break
                    
                results = self._search_google_scholar(query, page)
                
                if not results:
                    continue
                
                for result in results:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    text = title + " " + snippet
                    
                    # Extract case information
                    case_info = self.extractor.extract_case_details(text)
                    
                    if case_info and case_info['verdict'] != 'Unknown':
                        case_database.append(case_info)
                        
                        # Track judge statistics
                        if case_info['judge'] != "Unknown":
                            if case_info['judge'] not in judges_data:
                                judges_data[case_info['judge']] = []
                            judges_data[case_info['judge']].append(case_info)
                        
                        cases_found += 1
                        
                        if progress_callback:
                            progress_callback(cases_found)
                        
                        if cases_found >= num_cases:
                            break
        
        return case_database, judges_data
    
    def _search_google_scholar(self, query, page=0):
        """
        Search Google Scholar using SerpAPI
        
        Args:
            query: Search query
            page: Page number (0-based)
            
        Returns:
            list: Organic results or None if error
        """
        if not self.api_key:
            print("No API key found!")
            return None
            
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": self.api_key,
            "num": str(config.RESULTS_PER_PAGE),
            "start": str(page * config.RESULTS_PER_PAGE)
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return None
                
            data = response.json()
            
            if "error" in data:
                print(f"API Error: {data['error']}")
                return None
                
            return data.get("organic_results", [])
            
        except requests.exceptions.Timeout:
            print("Request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None"""
Database builder for fetching and storing criminal case data from Google Scholar
"""
import requests
import os
from dotenv import load_dotenv
from extractors import CaseExtractor
import config

# Load environment variables
load_dotenv()

class DatabaseBuilder:
    """Handles building the case database from Google Scholar"""
    
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY', '')
        self.extractor = CaseExtractor()
        
    def build_database(self, state, case_type_filter, num_cases, progress_callback=None):
        """
        Build database of criminal cases with defendant histories
        
        Args:
            state: State to search in
            case_type_filter: Type of cases to filter (or "All")
            num_cases: Number of cases to fetch
            progress_callback: Function to call with progress updates
            
        Returns:
            tuple: (case_database, judges_data)
        """
        case_database = []
        judges_data = {}
        
        # Build search queries
        search_queries = [query.format(state=state) for query in config.SEARCH_QUERIES]
        
        if case_type_filter != "All":
            search_queries = [q + f' "{case_type_filter}"' for q in search_queries]
        
        cases_found = 0
        
        for query_idx, query in enumerate(search_queries):
            if cases_found >= num_cases:
                break
                
            # Get multiple pages of results
            for page in range(config.PAGES_PER_QUERY):
                if cases_found >= num_cases:
                    break
                    
                results = self._search_google_scholar(query, page)
                
                if not results:
                    continue
                
                for result in results:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    text = title + " " + snippet
                    
                    # Extract case information
                    case_info = self.extractor.extract_case_details(text)
                    
                    if case_info and case_info['verdict'] != 'Unknown':
                        case_database.append(case_info)
                        
                        # Track judge statistics
                        if case_info['judge'] != "Unknown":
                            if case_info['judge'] not in judges_data:
                                judges_data[case_info['judge']] = []
                            judges_data[case_info['judge']].append(case_info)
                        
                        cases_found += 1
                        
                        if progress_callback:
                            progress_callback(cases_found)
                        
                        if cases_found >= num_cases:
                            break
        
        return case_database, judges_data
    
    def _search_google_scholar(self, query, page=0):
        """
        Search Google Scholar using SerpAPI
        
        Args:
            query: Search query
            page: Page number (0-based)
            
        Returns:
            list: Organic results or None if error
        """
        if not self.api_key:
            print("No API key found!")
            return None
            
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": self.api_key,
            "num": str(config.RESULTS_PER_PAGE),
            "start": str(page * config.RESULTS_PER_PAGE)
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return None
                
            data = response.json()
            
            if "error" in data:
                print(f"API Error: {data['error']}")
                return None
                
            return data.get("organic_results", [])
            
        except requests.exceptions.Timeout:
            print("Request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
