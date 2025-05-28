# Troubleshooting Guide

## Common Issues and Solutions

### No Cases Found / Empty Database

1. **Try Different Search Parameters**
   - Use "All" for case type instead of specific crimes
   - Increase the number of cases to search (try 100-200)
   - Some case types may have limited data in Google Scholar

2. **Google Scholar Limitations**
   - Academic database - not all criminal cases are indexed
   - Better coverage for appellate/significant cases
   - Local/minor cases may not appear

3. **Search Tips**
   - Start broad, then narrow down
   - Try major cities/counties in your state
   - Federal cases often have better coverage

### API Issues

**"Invalid API key"**
- Verify key at https://serpapi.com/manage-api-key
- Check for extra spaces in .env file
- Ensure no quotes around the key

**"Rate limit exceeded"**
- Free tier has limits - wait a few minutes
- Reduce "Cases to Analyze" number
- Consider upgrading API plan

**"No results returned"**
- Google Scholar may not have data for that query
- Try different state or case type
- Check your internet connection

### Application Crashes

**During Database Building:**
- Reduce number of cases to fetch
- Check Terminal for specific error messages
- May be network timeout - try again

**Memory Issues:**
- Close other applications
- Restart the app
- Reduce cases to under 100

### Poor Predictions

**"No similar cases found"**
- Your case combination may be unique
- Try broader case type categories
- Remove judge filter to get more matches

**Unrealistic Results:**
- Database may be too small - build larger dataset
- Check if similar cases actually match your client
- Remember: predictions based on available data only

### Debug Mode

Run with debug output:
```python
# Add to top of main.py after imports:
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show:
- API calls being made
- Data being extracted
- Matching logic

### Testing Your Setup

1. **Test API Connection:**
```python
import requests

api_key = "your_key_here"
response = requests.get(
    "https://serpapi.com/search",
    params={
        "engine": "google_scholar",
        "q": "criminal case California",
        "api_key": api_key
    }
)
print(response.json())
```

2. **Test with Known Cases:**
- Search for "California" + "All" case types
- Should find various criminal cases
- If nothing found, API or network issue

### Performance Tips

1. **Faster Searches:**
   - Start with 20-50 cases for testing
   - Use specific case types when possible
   - Build database once, analyze multiple times

2. **Better Matches:**
   - Be accurate with criminal history
   - Use exact charge names from dropdown
   - Include judge if known

### When to Contact Support

If you've tried the above and still have issues:
1. Check SerpAPI status page
2. Review Google Scholar's coverage
3. Open GitHub issue with:
   - Error messages
   - Steps to reproduce
   - Your Python version
   - Operating system

### Alternative Data Sources

If Google Scholar isn't sufficient:
- Consider adding other legal databases
- Check if your jurisdiction publishes case data
- Look into commercial legal research APIs

Remember: This tool analyzes publicly available data. Coverage and accuracy depend on what's indexed in Google Scholar.
