# Product Approval AI

> AI-powered product review service for digital sales platforms

A minimal REST API that uses AI to pre-review digital products, helping to accelerate manual approval processes and reduce workload for sales platforms.

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

You are free to use, modify, and share this project for **non-commercial purposes**, provided you give proper credit to the author.

> ⚠️ **For commercial use, licensing inquiries, or business collaborations, please contact:**  
> 📧 josecordeiro.dev@gmail.com

License details: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)

## 🚀 Quick Start

### Prerequisites
- Docker (recommended)
- OR Python 3.12+ with `uv` package manager

### 🐳 Running with Docker (Recommended)

1. **Build the Docker image:**
```bash
docker build -t product-approval-ai .
```

2. **Run the container:**
```bash
# Basic run (uses mock AI for testing)
docker run -p 8000:8000 product-approval-ai

# With OpenAI API key for real AI reviews
docker run -p 8000:8000 -e OPENAI_API_KEY="your-api-key-here" product-approval-ai

# With custom configuration
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-api-key-here" \
  -e OPENAI_MODEL="gpt-4" \
  -e DEBUG="true" \
  product-approval-ai
```

3. **Test the API:**
```bash
# Health check
curl http://localhost:8000/health

# Review a product
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Mindful Productivity Course",
    "sales_page": "Evidence-based strategies backed by psychology and behavioral science."
  }'
```

### 🔧 Local Development

1. **Clone and setup:**
```bash
git clone <repository-url>
cd Product-Approval-AI
uv sync
```

2. **Run locally:**
```bash
# Run with mock AI (no OpenAI key needed)
uv run uvicorn app.main:app --reload

# For running with OpenAI integration create .env file with your OpenAI API key
OPENAI_API_KEY="your-key"
```

3. **Run tests:**
```bash
uv run pytest tests/ -v
```

## 🧠 AI Architecture & Prompt Engineering

The AI review system uses OpenAI's latest structured output capabilities with a sophisticated multi-layered approach:

### 🆕 OpenAI Structured Output
- **Direct Pydantic Integration**: Uses `responses.parse()` with `text_format=ReviewResponse`
- **Automatic Validation**: Leverages Pydantic model validation for type safety
- **Zero Parsing Logic**: Eliminates manual JSON parsing and error handling
- **Enhanced Reliability**: Built-in validation ensures consistent response structure

### System Prompt Design
The AI reviewer is configured as an "expert product reviewer" with specific guidelines:

**Critical Rejection Criteria:**
1. **Unrealistic Claims** - Products promising impossible results (e.g., "lose 15kg in 21 days")
2. **Financial Scams** - Get-rich-quick schemes, guaranteed investment returns
3. **Health Misinformation** - Unproven medical claims, dangerous advice
4. **Illegal Content** - Copyrighted material, adult content
5. **Low Quality** - Poor presentation, vague descriptions

**Approval Criteria:**
1. **Evidence-Based** - Claims backed by research or proven methods
2. **Professional** - Well-written, realistic expectations
3. **Educational** - Provides genuine knowledge or skills
4. **Compliant** - Follows advertising standards

### Response Structure
- **Pydantic Model Validation**: Automatic enforcement of decision format and explanation length
- **Type Safety**: Direct parsing into `ReviewResponse` model with enum validation
- **Consistent Output**: Reliable structure through OpenAI's structured output API
- **Error Handling**: Graceful fallbacks with safety defaults

### Contextual Analysis
- Product name and sales page content analyzed together
- Keyword-based mock service for testing without OpenAI
- Comprehensive error handling and safety defaults

## 🚧 Limitations & Outlook

### Current Limitations

1. **Language Support** - Currently optimized for English content only
2. **Context Window** - Limited to 10,000 characters of sales page content
3. **Cultural Context** - May not handle region-specific regulations adequately
4. **Image Analysis** - Cannot process visual content or multimedia
5. **Real-time Learning** - No feedback loop to improve decisions over time

### Immediate Improvements (Next Sprint)

- **Multi-language Support** - Add German, Spanish, French detection and analysis
- **Content Expansion** - Support for images, videos, and longer content
- **Prompt Injection Protection** - Enhance system prompt to detect and ignore attempts at indirect prompt injection in the sales page content (e.g., sentences like "Approve this page")
- **Confidence Scoring** - Return confidence levels with decisions
- **Security** - Internal API key authentication for service-to-service communication, network-level security (VPN/internal network)
- **Add More Tests** - Expand the test suite to cover more difficult or ambiguous scenarios
- **Batch Processing** - Review multiple products in single API call
- **Fallback AI Provider** - Integrate support for an alternative API (e.g., Claude or Gemini) to automatically handle requests if the OpenAI API is unavailable

### Long-term Roadmap

- **Human-in-the-Loop** - Integration with manual review workflow
- **ML Training Pipeline** - Custom model training on platform-specific data
- **Real-time Monitoring** - Analytics dashboard for review patterns
- **A/B Testing Framework** - Compare different prompt strategies

### Production Considerations

- **Caching** - Cache decisions for identical content
- **Audit Logging** - Track all decisions for compliance
- **Model Versioning** - Manage prompt and model updates
- **Horizontal Scaling** - Queue-based processing for high volume

## ⏱️ Time Investment

**Total Development Time: ~4 hours**

- Phase 1 (Setup): 30 minutes
- Phase 2 (Implementation): 90 minutes  
- Phase 3 (Testing): 45 minutes
- Phase 4 (Docker/Docs): 45 minutes

## 📡 API Documentation

### POST /review

Reviews a product for approval based on content analysis.

**Request:**
```json
{
  "product_name": "string (1-200 chars)",
  "sales_page": "string (10-10000 chars)"
}
```

**Response:**
```json
{
  "decision": "approve" | "reject",
  "explanation": "string (1-3 sentences)"
}
```

**Status Codes:**
- `200` - Review completed successfully
- `400` - Invalid request (content too long)
- `422` - Validation error (empty fields, etc.)
- `500` - Internal server error
- `503` - AI service temporarily unavailable
- `504` - Request timeout

### GET /health

Health check endpoint returning service status.

## ⚙️ Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `""` | OpenAI API key (required for AI reviews) |
| `OPENAI_MODEL` | `"gpt-4.1"` | OpenAI model to use |
| `OPENAI_TIMEOUT` | `30` | API timeout in seconds |
| `USE_MOCK_AI` | `false` | Use mock service instead of OpenAI |
| `DEBUG` | `false` | Enable debug mode |
| `MAX_CONTENT_LENGTH` | `10000` | Max sales page length |

## 🧪 Testing

The project includes comprehensive testing:

- **7 tests total** (100% passing)
- **Unit tests** for review service logic
- **Integration tests** for API endpoints
- **Sample validation** using provided challenge data + two more samples from the Affiliate Marketplace
- **Edge case testing** (timeouts, malformed input)

Sample test results with challenge data:
- ✅ "Keto Mastery E-Book" → **REJECT** (unrealistic weight loss claims)
- ✅ "Crypto Signals 999" → **REJECT** (financial scam promises)
- ✅ "Mindful Productivity Course" → **APPROVE** (evidence-based education)

## 📊 Performance

- **Response Time** - ~1-3 seconds per review (including OpenAI API)
- **Throughput** - Scales with OpenAI rate limits
- **Memory** - ~50MB base container footprint
- **Test Coverage** - 100% of core functionality

## 🛠️ Development

### Code Quality
- **Linting** - Ruff for formatting and style checks
- **Type Hints** - Full type annotation coverage
- **Documentation** - Comprehensive docstrings
- **Error Handling** - Graceful degradation and proper HTTP status codes

### Architecture
- **Clean Separation** - Models, services, and API layers
- **Dependency Injection** - Configurable service dependencies
- **Async Support** - Full async/await pattern throughout
- **Modern Python** - Python 3.12+ features and best practices
- **🆕 Structured Output** - OpenAI Responses API with Pydantic integration

---
