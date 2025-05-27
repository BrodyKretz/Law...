# Troubleshooting Guide

## Common Issues and Solutions

### API Not Working / Still Showing Sample Data

1. **Check API Key is Loaded**
   - Look at the status bar at the bottom of the app
   - Should show "API Key: Loaded ✓"
   - If it shows "API Key: Not Found ✗", check your `.env` file

2. **Verify .env File**
   ```bash
   cat .env
   ```
   Should show:
   ```
   SERPAPI_KEY=your_actual_api_key_here
   ```

3. **Check Data Source Selection**
   - Make sure "Use Real API Data" is selected (not "Use Sample Data")

4. **API Key Issues**
   - Verify your API key is valid at https://serpapi.com/manage-api-key
   - Check you have remaining credits
   - Try the API key in their playground first

### Debug Mode

To see what's happening, run the app and check the Terminal output:
- API request details will be printed
- Response status codes will be shown
- Error messages will be more detailed

### Common Error Messages

**"No cases found for Judge X in Google Scholar"**
- Try a different judge name
- Google Scholar may not have indexed cases for that specific judge
- Try searching for more common judges or well-known cases

**"SerpAPI Error: Invalid API key"**
- Your API key is incorrect
- Double-check the key in your `.env` file
- Make sure there are no extra spaces or quotes

**"HTTP Error: 429"**
- Rate limit exceeded
- Wait a few minutes and try again
- Reduce the "Max Results" number

### Testing the API

Test your API key directly:
```python
import requests

api_key = "your_api_key_here"
url = "https://serpapi.com/search"
params = {
    "engine": "google_scholar",
    "q": "Judge California court",
    "api_key": api_key,
    "num": "5"
}

response = requests.get(url, params=params)
print(response.json())
```

### Still Not Working?

1. **Use Sample Data Mode**
   - Select "Use Sample Data" to test the app functionality
   - This proves the app itself is working

2. **Check Terminal for Errors**
   - Run the app from Terminal
   - Look for any Python errors or stack traces

3. **Verify Installation**
   ```bash
   pip list | grep google-search-results
   ```
   Should show: `google-search-results    2.4.2`

### Contact Support

If you're still having issues:
- Check SerpAPI documentation: https://serpapi.com/google-scholar-api
- Open an issue on GitHub with:
  - The error message
  - Terminal output
  - Your Python version (`python --version`)
