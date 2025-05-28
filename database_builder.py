"""
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
