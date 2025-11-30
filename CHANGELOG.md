# Changelog

All notable changes to the SudokuSolver project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2025.11.28] - 2025-11-28

### Added
- **Single-technique-per-step execution**: Step solve mode now executes one solving technique per call, cycling through all techniques in order
- **Comprehensive change tracking**: Complete record of all changes made during solving, including cells filled and candidates pruned per technique
- **Candidate grid display**: Visual display of candidate lists in empty cells (3×3 mini-grid layout) for enhanced solving visibility
- **Show Original toggle**: Toggle button to view original puzzle vs. current solved state in both Full Solve and Step Solve modes
- **Three-state solving system**: Step solve returns one of three states: "solving" (in progress), "solved" (puzzle complete), or "stuck" (no progress in full pass)
- **Pass progress tracking**: System tracks whether any changes occurred during a complete pass through all solving techniques to detect stuck state
- **Mobile responsive design**: Optimized UI scaling for iPhone SE (375x667 viewport) with reduced font sizes, adjusted spacing, and proper grid dimensions

### Changed
- **Step solve execution model**: Changed from applying all techniques to applying one technique per invocation, maintaining technique index across serialization
- **Step solve return type**: Now returns `Tuple[Literal["solving", "solved", "stuck"], Dict[str, Any]]` instead of boolean, including change record
- **Message formatting**: Improved status message format with status-first structure and bold status lines
- **Debug mode UI**: Removed debug level selection from frontend UI (still fully supported via API, defaults to silent mode)
- **Message box styling**: Consistent width matching grid, left alignment, and bold status lines across both Full Solve and Step Solve modes
- **Result display unification**: Full Solve and Step Solve modes now use consistent message box styling and display format
- **Step solve state management**: Step solve mode now properly tracks and displays solving state with appropriate button visibility

### Fixed
- **Stuck state detection**: Step solve correctly detects "stuck" state when no progress is made during a complete pass through all techniques
- **Initial candidate display**: Candidates are correctly displayed in step solve mode on first grid display before any solving steps
- **Mobile UI scaling**: Resolved grid dimension and spacing issues on iPhone SE to eliminate horizontal scrolling
- **Grid display consistency**: Fixed grid appearance differences between Full Solve and Step Solve modes
- **Empty cell rendering**: Fixed "0" character display in empty cells when Show Original is active
- **Change record formatting**: Improved message formatting to show technique name even when no changes are made ("attempted but nothing found")

### Removed
- **Debug mode selection UI**: Removed debug level radio buttons from SolveForm (functionality still available via API)
- **one_pass_solve method**: Removed unused method from SudokuSolver class

### Technical Details
- Step solve technique index persists through serialization/deserialization
- Change tracking records include technique name, list of cells filled (with row/col/value), and list of candidates pruned (with row/col/candidate)
- Solver state fully serializable including technique index and pass progress flag
- Candidate grids extracted and displayed in real-time during step solving
- Redis-backed session management maintains complete solver state between step calls

## Previous Releases

### [v2025.11.27b] - 2025-11-27
- Fixed candidate display initialization in step solve mode
- Improved change tracking implementation

### [v2025.11.27a] - 2025-11-27
- Initial implementation of step solve mode with single-technique execution
- Added change tracking infrastructure

### [v2025.11.26] - 2025-11-26
- Redis-backed stepwise solving (experimental)
- Session management endpoints
- Docker Compose production configuration with Redis

### Earlier Releases
See [README.md](README.md) for historical improvements and feature additions.

