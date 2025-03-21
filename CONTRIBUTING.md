# Contributing to Preload Measurement MVP

Thank you for your interest in contributing to the Preload Measurement MVP project! This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic knowledge of dental implant systems
- Familiarity with Streamlit (for UI contributions)

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/preload-measurement-mvp.git
   cd preload-measurement-mvp
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Run the application locally**
   ```bash
   streamlit run app/main.py
   ```

## Development Workflow

### Branching Strategy

- `main`: Stable production code
- `develop`: Integration branch for features
- `feature/feature-name`: For new features
- `bugfix/bug-name`: For bug fixes
- `doc/description`: For documentation updates

### Creating a New Feature

1. **Create a new branch from `develop`**
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes following the coding standards**

3. **Run tests and linting**
   ```bash
   pytest
   flake8
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push your branch and create a pull request**
   ```bash
   git push -u origin feature/your-feature-name
   ```

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length: 88 characters
- Use docstrings for all functions and classes
- Use type hints where possible

### Commit Messages

Follow the Conventional Commits specification:
- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation only changes
- `style:` - Changes that do not affect the meaning of the code
- `refactor:` - Code changes that neither fix a bug nor add a feature
- `test:` - Adding or correcting tests
- `chore:` - Changes to the build process or auxiliary tools

Example: `feat: add preload calculation for Nobel Biocare implants`

## Testing

- Write unit tests for all new functionality
- Tests should be placed in the `tests/` directory with a corresponding structure to the module being tested
- Maintain at least 80% test coverage

## Documentation

- Update the README.md with new features or usage instructions
- Document all functions, classes, and complex code blocks
- Update the Design Document if architectural changes are made

## Pull Request Process

1. Ensure all tests pass and code meets linting standards
2. Update relevant documentation
3. Obtain review from at least one core team member
4. Once approved, your PR will be merged by a maintainer

## Code of Conduct

- Be respectful and inclusive in all interactions
- Provide constructive feedback on pull requests
- Help fellow contributors when possible

## Questions and Support

If you have questions or need support, please:
1. Check existing issues before creating a new one
2. Provide clear, concise information when reporting issues
3. Include steps to reproduce any bugs

Thank you for contributing to the Preload Measurement MVP project! 