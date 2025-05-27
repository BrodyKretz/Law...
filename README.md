# Judicial Decision Analyzer

A Python application that analyzes judicial decisions and predicts case outcomes based on historical data from Google Scholar.

## Features

- **State-based Judge Selection**: Currently supports California with infrastructure for expanding to other states
- **Judge Case History Display**: View historical cases handled by selected judges
- **Real Google Scholar Integration**: Fetches actual court case data using SerpAPI
- **Data Source Options**: Choose between real API data or sample data
- **Configurable Results**: Set maximum number of results to fetch (1-20)
- **Case Outcome Prediction**: Predict likely outcomes based on:
  - Judge's historical decisions
  - Client's criminal history
  - Case type
- **Clean GUI Interface**: Built with Tkinter for easy use
- **Structured Data Display**: Table view of judge's case history including:
  - Case types
  - Verdicts
  - Punishments
  - Defendant criminal history

## Installation

### Prerequisites

- Python 3.8 or higher
- macOS (tested on macOS, should work on other platforms)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/judicial-decision-analyzer.git
cd judicial-decision-analyzer
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API key:
   - Get a SerpAPI key from [https://serpapi.com/](https://serpapi.com/)
   - Create a `.env` file in the project root:
   ```
   SERPAPI_KEY=your_api_key_here
   ```

## Usage

Run the application:
```bash
python main.py
```

### How to Use

1. **Select State**: Choose California from the dropdown (more states coming soon)
2. **Select Judge**: Choose a judge from the available list
3. **Choose Data Source**: 
   - "Use Real API Data" - Fetches from Google Scholar (requires API key)
   - "Use Sample Data" - Uses built-in demo data
4. **Set Max Results**: Choose how many results to fetch (1-20)
5. **Fetch Data**: Click "Fetch Judge Data" to load the judge's case history
6. **Review History**: Examine the judge's past cases in the table
7. **Predict Outcome**: 
   - Enter your client's criminal history (felonies and misdemeanors)
   - Select the case type
   - Click "Predict Outcome" to see the analysis

## Project Structure

```
judicial-decision-analyzer/
│
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env                # API keys (create this, don't commit)
├── .gitignore          # Git ignore file
│
└── data/               # Data storage (future implementation)
    └── judges.json     # Cached judge data
```

## API Integration

The application is designed to use the Google Scholar API via SerpAPI. Currently, it uses sample data for demonstration. To enable real API calls:

1. Uncomment the API call code in the `fetch_from_google_scholar` method
2. Implement data parsing logic for the API responses
3. Structure the data according to the expected format

## Future Enhancements

- [ ] Add support for all 50 states
- [ ] Implement real Google Scholar API integration
- [ ] Add machine learning model for more accurate predictions
- [ ] Export functionality for case analysis reports
- [ ] Historical trend analysis charts
- [ ] Database integration for caching judge data
- [ ] Advanced filtering options
- [ ] Batch analysis capabilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for informational purposes only and should not be used as a substitute for legal advice. Always consult with a qualified attorney for legal matters.

## Support

For issues or questions, please open an issue on GitHub or contact the maintainers.
