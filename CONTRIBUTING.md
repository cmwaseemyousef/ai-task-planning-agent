# Contributing to AI Task Planning Agent

Thank you for your interest in contributing to the AI Task Planning Agent project!

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment (recommended)

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/cmwaseemyousef/ai-task-planning-agent.git
   cd ai-task-planning-agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Code Style and Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Maximum line length: 88 characters
- Use meaningful variable and function names

### Testing
- Write unit tests for new features
- Maintain test coverage above 80%
- Run tests before submitting PR:
  ```bash
  pytest tests/ --cov=agent
  ```

### Git Workflow
1. Create feature branch from `master`
2. Make focused, atomic commits
3. Write clear commit messages
4. Submit pull request with description

## Project Structure

```
├── agent/          # Core AI planning logic
├── database/       # Data models and operations
├── tools/          # External API integrations
├── web/           # Frontend templates and assets
├── tests/         # Test suite
└── docs/          # Documentation
```

## Submitting Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation if needed

3. **Test Your Changes**
   ```bash
   pytest tests/
   python main.py  # Manual testing
   ```

4. **Submit Pull Request**
   - Clear description of changes
   - Reference any related issues
   - Include screenshots for UI changes

## Reporting Issues

When reporting bugs or requesting features:
- Use GitHub Issues
- Provide clear reproduction steps
- Include error messages and logs
- Specify your environment details

## Questions?

Feel free to open an issue for any questions about contributing to this project.