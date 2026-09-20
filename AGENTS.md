# Vienna Public Transport AI Agent Instructions

This file provides instructions for AI agents working with the Vienna Public Transport codebase.

## Project Overview

Vienna Public Transport is a custom Home Assistant integration for real-time public transport departures in Vienna.

## Technical Stack

### Backend

- Language: Python `3.14.x`
- Framework: Home Assistant
- Package Manager: `uv`
- Testing: Pytest
- Linting: Ruff
- Type Checking: MyPy

### Frontend

- Language: TypeScript `5.9.x`
- Framework: Lit 
- Package Manager: `npm`
- Build Tool: Vite
- Testing: Vitest

## Repository Structure

- `custom_components/vienna_transport/`: Backend Home Assistant integration
- `src/`: Frontend Lovelace card
- `tests/`: Unit and integration tests for the backend
- `pyproject.toml`: Backend dependencies and scripts
- `package.json`: Frontend dependencies and scripts

## Core Architecture

### Backend

The core backend architecture is described in `custom_components/vienna_transport/ARCHITECTURE.md`.

### Frontend

- Main card: `src/transport-card.ts` (a `LitElement` that renders the departures)
- Card editor: `src/transport-card-editor.ts` (for configuration)
- Model: `src/api.ts`

## Verification Commands

### Backend

Run these commands to verify changes made to backend code:

- Run `uv sync --extra dev` to install backend dependencies
- Run `uv run pytest` to run backend tests
- Run `uv run pytest --cov` to run backend tests with coverage
- Run `uv run mypy` to type check backend code with MyPy
- Run `uv run ruff check` to check backend code with Ruff
- Run `uv run ruff format` to format backend code with Ruff
 
### Frontend

Run these commands to verify changes made to frontend code:

- Run `npm run build` to build the frontend code
- Run `npm run test` to run frontend tests
- Run `npm run format` to format frontend code with Prettier

## Version Control Guidelines (Git)

- Use conventional commit messages 
- Include a scope in the commit message
- Add a body to the commit message if necessary
