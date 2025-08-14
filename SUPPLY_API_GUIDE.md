# Supply Result Processing API Guide

This guide explains how to use the new supply result processing API endpoints that intelligently merge supply exam results with existing regular results.

## Features

✅ **Smart Grade Overwriting**: Only overwrites regular grades when supply grades are better  
✅ **Attempt Tracking**: Automatically counts and tracks attempts per subject  
✅ **Subject-Level Matching**: Matches results by subject code for precise updates  
✅ **Improvement Detection**: Identifies and logs grade improvements  
✅ **Firebase Integration**: Real-time updates to Firestore database  
✅ **Comprehensive Logging**: Detailed logs of all merge operations  

## API Endpoints

### 1. Upload Supply PDF (`/upload-supply-pdf`)

**Method**: `POST`  
**Content-Type**: `multipart/form-data`  
**Authentication**: Requires API key

**Request Parameters**:
```
pdf: [File] - The supply result PDF file
format: [String] - Parser format ('jntuk' or 'autonomous')
```

**Example Usage**:
```bash
curl -X POST "https://your-app-url.com/upload-supply-pdf" \
  -H "X-API-Key: your-api-key" \
  -F "pdf=@supply_results.pdf" \
  -F "format=jntuk"
```

**Response Example**:
```json
{
  "message": "Successfully processed supply results with smart merge.",
  "result": {
    "status": "success",
    "stats": {
      "total_processed": 150,
      "students_updated": 45,
      "students_added": 5,
      "supply_overwrites": 32,
      "total_attempts_tracked": 78
    },
    "improvement_report": {
      "total_improvements": 32,
      "grade_improvements": {
        "F_to_D": 15,
        "F_to_C": 10,
        "D_to_C": 5,
        "C_to_B": 2
      }
    }
  },
  "firebase": {
    "enabled": true,
    "processing_time": 2.34,
    "storage_url": "https://storage.googleapis.com/..."
  }
}
```

### 2. Supply Improvement Report (`/api/supply-improvement-report`)

**Method**: `GET`  
**Authentication**: Requires API key

**Query Parameters**:
```
days: [Integer] - Number of days to look back (default: 30)
format: [String] - Filter by format type ('jntuk' or 'autonomous', optional)
```

**Example Usage**:
```bash
curl -X GET "https://your-app-url.com/api/supply-improvement-report?days=60&format=jntuk" \
  -H "X-API-Key: your-api-key"
```

**Response Example**:
```json
{
  "message": "Supply improvement report generated successfully",
  "report": {
    "summary": {
      "total_students_improved": 127,
      "total_grade_improvements": 245,
      "success_rate": 78.5,
      "most_improved_subject": "CS101"
    },
    "grade_distribution": {
      "F_to_D": 45,
      "F_to_C": 32,
      "D_to_C": 28,
      "C_to_B": 15
    },
    "subject_wise_improvements": {
      "CS101": {"improvements": 23, "success_rate": 82.1},
      "MA101": {"improvements": 18, "success_rate": 75.0}
    }
  }
}
```

## How Smart Merge Works

### 1. Grade Hierarchy
The system uses this grade hierarchy for comparison:
```
O > A+ > A > B+ > B > C > D > F
```

### 2. Merge Logic
```python
# For each student in supply results:
1. Find existing student record in Firebase
2. For each subject in supply results:
   a. Check if subject exists in regular results
   b. Compare grades using hierarchy
   c. If supply grade > regular grade:
      - Update grade to supply grade
      - Increment attempt count
      - Log improvement
   d. If new subject:
      - Add subject with attempt count = 1
```

### 3. Attempt Tracking
```python
# Attempt counting logic:
- Regular result = Attempt #1
- First supply improvement = Attempt #2
- Second supply improvement = Attempt #3
- And so on...
```

## Integration Examples

### Frontend Integration (JavaScript)

```javascript
// Upload supply PDF
async function uploadSupplyPDF(file, format) {
  const formData = new FormData();
  formData.append('pdf', file);
  formData.append('format', format);
  
  const response = await fetch('/upload-supply-pdf', {
    method: 'POST',
    headers: {
      'X-API-Key': 'your-api-key'
    },
    body: formData
  });
  
  const result = await response.json();
  console.log('Supply processing result:', result);
  return result;
}

// Get improvement report
async function getImprovementReport(days = 30) {
  const response = await fetch(`/api/supply-improvement-report?days=${days}`, {
    headers: {
      'X-API-Key': 'your-api-key'
    }
  });
  
  const report = await response.json();
  console.log('Improvement report:', report);
  return report;
}
```

### Python Integration

```python
import requests

def upload_supply_pdf(pdf_path, format_type, api_key):
    url = "https://your-app-url.com/upload-supply-pdf"
    
    with open(pdf_path, 'rb') as f:
        files = {'pdf': f}
        data = {'format': format_type}
        headers = {'X-API-Key': api_key}
        
        response = requests.post(url, files=files, data=data, headers=headers)
        return response.json()

def get_improvement_report(days=30, format_filter=None, api_key=None):
    url = "https://your-app-url.com/api/supply-improvement-report"
    params = {'days': days}
    if format_filter:
        params['format'] = format_filter
    
    headers = {'X-API-Key': api_key}
    response = requests.get(url, params=params, headers=headers)
    return response.json()
```

## Database Structure

### Student Document (After Supply Processing)
```json
{
  "student_id": "20R01A0501",
  "name": "John Doe",
  "subjects": {
    "CS101": {
      "grade": "C",
      "credits": 4,
      "result_type": "SUPPLY",
      "attempts": 2,
      "attempt_history": [
        {
          "attempt": 1,
          "grade": "F",
          "type": "REGULAR",
          "timestamp": "2024-01-15T10:30:00Z"
        },
        {
          "attempt": 2,
          "grade": "C",
          "type": "SUPPLY",
          "timestamp": "2024-03-20T14:45:00Z",
          "improvement": true,
          "previous_grade": "F"
        }
      ]
    }
  },
  "metadata": {
    "last_updated": "2024-03-20T14:45:00Z",
    "total_attempts": 2,
    "supply_improvements": 1
  }
}
```

## Error Handling

### Common Error Responses

```json
// Missing required fields
{
  "error": "Missing required fields (pdf, format).",
  "status": 400
}

// Invalid format
{
  "error": "Invalid format type. Must be 'jntuk' or 'autonomous'.",
  "status": 400
}

// Supply processing not available
{
  "error": "Supply processing functionality not available.",
  "status": 503
}

// Internal server error
{
  "error": "Internal server error while processing supply PDF.",
  "status": 500
}
```

## Best Practices

1. **Always validate PDF format** before uploading
2. **Check response status** before processing results
3. **Use appropriate format parameter** ('jntuk' or 'autonomous')
4. **Monitor improvement reports** regularly for analytics
5. **Handle errors gracefully** in your frontend application

## Testing

You can test the supply processing using the included test file:

```bash
python test_supply_logic.py
```

This will demonstrate:
- Grade improvement detection
- Supply merge simulation
- API usage examples

## Deployment Notes

- The supply processing functionality is automatically loaded when `batch_pdf_processor.py` is available
- All supply processing is logged for monitoring and debugging
- Firebase integration is required for smart merge functionality
- PDF files are automatically uploaded to Firebase Storage

## Support

For questions or issues with supply processing:
1. Check the application logs for detailed error messages
2. Verify Firebase configuration is correct
3. Ensure PDF format matches the selected parser type
4. Review the improvement report for processing statistics
