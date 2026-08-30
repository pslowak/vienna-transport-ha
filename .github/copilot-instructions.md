# Copilot Code Review Instructions

## Project Overview

Vienna Transport is a Home Assistant custom integration for real-time public transport departures in Vienna, Austria. It
provides a backend written in Python that fetches data from the Wiener Linien API and a frontend Lit card written in 
TypeScript to display departures.

The codebase is organized into key architectural layers:

### Root Folders

- `custom_components/vienna_transport/`: Backend Home Assistant integration
- `src/`: Frontend Lovelace card
- `tests/`: Unit and integration tests for the backend

### Core Architecture

#### Backend

The core backend architecture is described in `custom_components/vienna_transport/architecture.md`.

#### Frontend

The main card component is `src/transport-card.ts`, which is a `LitElement` that renders the departures.
The card uses an editor `src/transport-card-editor.ts` for configuration. 

## Code Review Methodology

Walk through these layers in order when reviewing any change:

1. **Scope and Intent**: Understand the purpose of the change and its impact on the integration.
2. **Architecture**: Ensure the change respects the architectural boundaries and does not introduce technical debt.
3. **Correctness**: Verify that the change is correct, secure, and performant. Check for proper error handling, validation, and accessibility.
4. **Code Quality**: Evaluate the overall quality of the code, including maintainability, readability, and adherence to best practices which are idiomatic to the language and framework.
5. **Improvements**: Suggest any improvements or refactoring that could enhance the codebase.
6. **Testing**: Verify that the change is properly tested. 
7. **Documentation**: Ensure that the change is well-documented and that the documentation is up-to-date.

### Minimal Change Principle

- Consider if the change is necessary and if it can be simplified.
- Avoid over-engineering and unnecessary complexity.
- Flag scope creeps (changes to files not required for the task add risk without benefit).
