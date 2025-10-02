# TradingAgents Setup Guide

## Quick Start

### 1. Install Dependencies

The project uses Python 3.10+ and requires several packages. Install them using:

```bash
# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

### 2. Set Up API Keys

The project requires API keys for data fetching:

```bash
# Required for financial data
export FINNHUB_API_KEY="your_finnhub_api_key"

# Required for LLM operations
export OPENAI_API_KEY="your_openai_api_key"

# Optional: Use Google's Gemini models
export GOOGLE_API_KEY="your_google_api_key"
```

**Getting API Keys:**
- FinnHub: Sign up at https://finnhub.io/ (free tier available)
- OpenAI: Get key from https://platform.openai.com/
- Google: Get key from https://makersuite.google.com/app/apikey

### 3. Configure Data Directory (Optional)

If you want to use cached/offline data:

```bash
export TRADINGAGENTS_DATA_DIR="/path/to/your/data"
```

The default is `./data` relative to the project.

### 4. Run the CLI

```bash
# Interactive CLI with prompts
python -m cli.main

# Or run the example script
python main.py
```

## Configuration Options

Edit `tradingagents/default_config.py` or create a custom config:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"  # or "openai", "anthropic"
config["deep_think_llm"] = "gemini-2.0-flash"
config["quick_think_llm"] = "gemini-2.0-flash"
config["max_debate_rounds"] = 2  # More thorough analysis
config["online_tools"] = True  # Use real-time API data

# Initialize
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

## Project Structure

```
TradingAgents/
├── cli/                      # Command-line interface
│   ├── main.py              # CLI entry point
│   └── utils.py             # CLI utilities
├── tradingagents/
│   ├── agents/              # AI agent implementations
│   │   ├── analysts/       # Market, news, social, fundamentals
│   │   ├── researchers/    # Bull and bear researchers
│   │   ├── risk_mgmt/      # Risk management team
│   │   └── trader/         # Trading execution
│   ├── dataflows/          # Data fetching and processing
│   │   ├── json_validator.py  # JSON error handling (NEW)
│   │   ├── finnhub_utils.py   # FinnHub data
│   │   ├── reddit_utils.py    # Reddit sentiment
│   │   └── interface.py       # Unified data interface
│   └── graph/              # LangGraph workflow
│       └── trading_graph.py   # Main orchestration
├── data/                    # Local data cache (optional)
├── results/                 # Analysis results
├── main.py                  # Example usage script
└── requirements.txt         # Python dependencies
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
# Install missing dependencies
pip install -r requirements.txt
```

### "Bad Unicode escape in JSON"
This has been fixed! The project now handles Unicode errors gracefully. If you still see this:
```bash
# Test the fixes
python3 test_json_basic.py

# Validate your data files
python3 -c "from tradingagents.dataflows.json_validator import validate_data_directory; print(validate_data_directory('./data'))"
```

### "File not found" errors
The project works with both online and offline data:
- **Online mode** (default): Set `online_tools=True` in config
- **Offline mode**: Requires data files in `data/` directory

### API rate limits
If you hit rate limits:
1. Use cached data by setting `online_tools=False`
2. Reduce `max_debate_rounds` and `max_risk_discuss_rounds`
3. Add delays between API calls

## Development Workflow

### Running Tests
```bash
# Basic JSON handling tests
python3 test_json_basic.py

# Full integration tests (requires dependencies)
python3 test_json_fixes.py
```

### Debugging
Enable debug mode to see agent reasoning:
```python
ta = TradingAgentsGraph(debug=True, config=config)
```

This will print all agent messages and tool calls.

### Adding Custom Analysts
1. Create new analyst in `tradingagents/agents/analysts/`
2. Register in `tradingagents/graph/setup.py`
3. Add to `selected_analysts` list

## Performance Tips

1. **Use faster models for testing**:
   - `gpt-4o-mini` instead of `gpt-4o`
   - `gemini-2.0-flash` instead of `gemini-2.0-pro`

2. **Reduce analysis depth**:
   ```python
   config["max_debate_rounds"] = 1
   config["max_risk_discuss_rounds"] = 1
   ```

3. **Cache data locally**:
   - Run once with `online_tools=True`
   - Save results to `data/` directory
   - Switch to `online_tools=False` for subsequent runs

## Examples

### Basic Analysis
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG)
final_state, decision = ta.propagate("AAPL", "2024-05-10")
print(f"Decision: {decision}")
```

### Custom Configuration
```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "google"
config["deep_think_llm"] = "gemini-2.0-flash"
config["max_debate_rounds"] = 3

ta = TradingAgentsGraph(
    selected_analysts=["market", "news", "fundamentals"],
    debug=True,
    config=config
)
```

### Batch Analysis
```python
tickers = ["AAPL", "GOOGL", "MSFT"]
dates = ["2024-05-10", "2024-05-11", "2024-05-12"]

for ticker in tickers:
    for date in dates:
        _, decision = ta.propagate(ticker, date)
        print(f"{ticker} on {date}: {decision}")
```

## Support

- GitHub Issues: https://github.com/TauricResearch/TradingAgents/issues
- Discord: https://discord.com/invite/hk9PGKShPK
- Documentation: See README.md

## License

See LICENSE file in the project root.
