# Contributing to HireScope

Thank you for your interest in contributing to HireScope! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

- Check if the issue already exists
- Include steps to reproduce
- Include system information (Python version, OS)
- Include relevant error messages

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Testing

- Add unit tests for new features
- Ensure existing tests pass
- Test with different Python versions

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/hirescope.git
cd hirescope

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .
pip install pytest pytest-cov

# Run tests
pytest
```

## Areas for Contribution

- Additional file format support (RTF, TXT)
- Performance optimizations
- Documentation improvements
- Bug fixes
- New features
- UI/UX improvements

## Questions?

Feel free to open an issue for discussion or reach out to contact@gsdat.work

## License

By contributing, you agree that your contributions will be licensed under the MIT License.