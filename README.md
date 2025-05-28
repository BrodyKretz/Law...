# Criminal Case Outcome Predictor

A Python application that helps attorneys predict case outcomes by analyzing similar criminal cases from Google Scholar. The system finds defendants with similar criminal histories and charges to provide data-driven predictions.

## Key Features

### For Attorneys:
- **Build Case Database**: Search Google Scholar for criminal cases with defendant histories
- **Find Similar Cases**: Automatically matches cases based on:
  - Criminal charge type
  - Defendant's prior felonies/misdemeanors
  - Prior conviction count
  - Assigned judge (if known)
- **Outcome Prediction**: Provides probability analysis:
  - Conviction rates for similar cases
  - Average sentences
  - Risk assessment (High/Moderate/Low)
  - Judge-specific statistics
- **Comprehensive Reports**: Three analysis tabs:
  - Similar Cases table
  - Detailed prediction analysis
  - Judge statistics across all cases

## How It Works

1. **Database Building**: Searches Google Scholar for criminal cases containing:
   - Defendant criminal histories
   - Verdicts and sentences
   - Judge information
   - Case details

2. **Case Matching**: When you input your client's information, it finds the most similar cases based on:
   - Matching charge types
   - Similar criminal history (prior felonies, misdemeanors)
   - Same judge (if specified)

3. **Prediction Analysis**: Based on similar cases, predicts:
   - Likelihood of guilty verdict
   - Expected sentence range
   - Success rate of plea deals
   - Judge-specific tendencies

## Installation

### Prerequisites

- Python 3.8 or higher
- macOS (tested on macOS, should work on other platforms)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/criminal-case-predictor.git
cd criminal-case-predictor
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

### Step-by-Step Guide:

1. **Build Case Database**:
   - Select state (e.g., California)
   - Choose case type filter (or "All")
   - Set number of cases to analyze (10-200)
   - Click "Build Case Database"
   - Wait for progress bar to complete

2. **Enter Your Client's Information**:
   - Prior Felonies: Number of previous felony convictions
   - Prior Misdemeanors: Number of previous misdemeanor convictions
   - Prior Convictions: Total conviction count
   - Current Charge: Select from dropdown
   - Judge (optional): Select if known

3. **Analyze Case**:
   - Click "Analyze Case Outcome"
   - Review the three tabs:
     - **Similar Cases**: See actual cases similar to yours
     - **Prediction Analysis**: Detailed outcome predictions
     - **Judge Statistics**: Performance data for all judges

## Understanding the Results

### Risk Assessment:
- **HIGH RISK (>75% conviction rate)**: Strong recommendation for plea negotiations
- **MODERATE RISK (50-75%)**: Consider both trial and plea options
- **LOWER RISK (<50%)**: Trial may be viable

### Prediction Report Includes:
- Verdict probabilities (Guilty/Not Guilty/Plea Deal)
- Sentencing analysis (average, min, max sentences)
- Criminal history impact on outcomes
- Judge-specific conviction rates
- Tailored recommendations

## Example Use Case

An attorney representing a client charged with burglary who has 2 prior felonies:
1. Build database with 100 California burglary cases
2. Enter client's criminal history
3. System finds 25 similar cases
4. Results show: 68% conviction rate, average 4.2 years sentence
5. Recommendation: Consider plea negotiations

## Project Structure

```
criminal-case-predictor/
│
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env                # API keys (create this, don't commit)
├── .gitignore          # Git ignore file
└── TROUBLESHOOTING.md  # Common issues and solutions
```

## Important Notes

- **Data Source**: All case data comes from Google Scholar
- **Accuracy**: Predictions based on available public case data
- **Privacy**: No client data is stored or transmitted
- **Legal Disclaimer**: This tool provides statistical analysis only. Always rely on professional legal judgment.

## Limitations

- Limited to cases indexed by Google Scholar
- Criminal history extraction may not be 100% accurate
- Some judges may have limited case data available
- Not a substitute for legal expertise

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for informational purposes only and should not be used as a substitute for legal advice. Case outcomes depend on many factors not captured in this analysis. Always consult with qualified legal counsel for case strategy.
