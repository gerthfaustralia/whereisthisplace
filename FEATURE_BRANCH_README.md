# OpenAI-Default Feature Branch

**Branch:** `feature/openai-default-mode`

## 🎯 Purpose

This feature branch makes OpenAI the **default prediction method** instead of the model. This allows testing OpenAI responses while the model and training database mature.

## 🔄 Behavior Changes

### Before (main branch):
- **Default**: Use model prediction
- **mode=openai**: Use OpenAI only if model confidence is low or bias detected
- **Fallback**: OpenAI used when model fails or has low confidence

### After (this branch):
- **Default**: Use OpenAI (if API key available)
- **mode=model**: Force model prediction only
- **mode=openai**: Use OpenAI (same as default)
- **Fallback**: Use model if OpenAI fails

## 🛠️ Setup

1. **Set OpenAI API Key:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

2. **Start your API server:**
   ```bash
   # Make sure you're on the feature branch
   git checkout feature/openai-default-mode
   
   # Start your API (however you normally do it)
   # e.g., docker-compose up, or python -m uvicorn api.main:app
   ```

## 🧪 Testing

### Quick Test
```bash
# Test the new default behavior
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "photo=@eiffel.jpg" | jq '.'

# Should return source: "openai" (if API key is set)
```

### Comprehensive Testing
```bash
# Run the feature branch test suite
python scripts/test_openai_default.py eiffel.jpg

# This will test:
# - Default mode (should use OpenAI)
# - Explicit model mode (should use model)
# - Explicit OpenAI mode (should use OpenAI)
# - Side-by-side comparison of predictions
```

### Manual Testing Scenarios

1. **Default OpenAI Usage:**
   ```bash
   curl -X POST "http://localhost:8000/predict" \
     -F "photo=@eiffel.jpg" | jq '.prediction.source'
   # Expected: "openai"
   ```

2. **Force Model Usage:**
   ```bash
   curl -X POST "http://localhost:8000/predict" \
     -F "photo=@eiffel.jpg" \
     -F "mode=model" | jq '.prediction.source'
   # Expected: "model"
   ```

3. **Compare Predictions:**
   ```bash
   # Get OpenAI prediction (default)
   curl -X POST "http://localhost:8000/predict" \
     -F "photo=@eiffel.jpg" | jq '.prediction | {source, lat, lon, score}'
   
   # Get model prediction
   curl -X POST "http://localhost:8000/predict" \
     -F "photo=@eiffel.jpg" \
     -F "mode=model" | jq '.prediction | {source, lat, lon, score}'
   ```

## 📊 Expected Results

### With OpenAI API Key Set:
- **Default requests**: `source: "openai"`, `score: 0.95`
- **Model requests**: `source: "model"`, `score: <model_confidence>`
- **Original score preserved**: When using OpenAI, `original_score` shows model confidence

### Without OpenAI API Key:
- **All requests**: `source: "model"` (fallback behavior)
- **Warning added**: `bias_warning: "OpenAI unavailable: ..."`

## 🔍 Response Format

```json
{
  "status": "success",
  "filename": "eiffel.jpg",
  "prediction": {
    "lat": 48.858890,
    "lon": 2.320041,
    "score": 0.95,
    "source": "openai",
    "confidence_level": "high",
    "original_score": 0.9738,  // Model's original confidence
    "bias_warning": null
  },
  "message": "Prediction completed successfully"
}
```

## 🚀 Deployment Considerations

### Environment Variables
```bash
# Required for OpenAI functionality
OPENAI_API_KEY=your-key-here

# Optional: Custom OpenAI endpoint
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Cost Implications
- **Higher API costs**: Every prediction now uses OpenAI Vision API
- **Token usage**: ~400-500 tokens per image prediction
- **Rate limits**: OpenAI API rate limits apply

### Performance
- **Latency**: OpenAI requests add ~2-5 seconds per prediction
- **Reliability**: Depends on OpenAI API availability
- **Fallback**: Model predictions used if OpenAI fails

## 🔄 Switching Back to Model-Default

To revert to model-default behavior:
```bash
git checkout main
# or merge main into your branch and resolve conflicts
```

## 📝 Development Notes

### Code Changes Made:
1. **`api/routes/predict.py`**: Modified prediction logic to default to OpenAI
2. **Error handling**: Enhanced fallback when OpenAI fails
3. **Response format**: Added `original_score` field for comparison
4. **Documentation**: Updated function docstrings

### Testing Scripts:
- **`scripts/test_openai_default.py`**: Comprehensive feature testing
- **`scripts/debug_openai.py`**: Direct OpenAI API testing
- **`scripts/force_openai_test.py`**: Force OpenAI usage scenarios

## 🎯 Use Cases

This branch is ideal for:
- **Testing OpenAI accuracy** vs your model
- **Gathering OpenAI predictions** for training data
- **Comparing prediction quality** side-by-side
- **Validating OpenAI integration** before production
- **Building confidence** in OpenAI as primary predictor

## ⚠️ Important Notes

1. **Cost Monitoring**: Watch OpenAI API usage and costs
2. **Rate Limits**: Be aware of OpenAI API rate limits
3. **Fallback Testing**: Ensure model fallback works when OpenAI fails
4. **Data Collection**: Consider logging both predictions for analysis
5. **Performance**: Monitor response times with OpenAI as default

---

**Next Steps:**
1. Test the feature branch thoroughly
2. Compare prediction accuracy between model and OpenAI
3. Monitor costs and performance
4. Decide when to merge or keep as separate deployment 