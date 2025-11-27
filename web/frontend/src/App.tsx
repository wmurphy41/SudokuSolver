/**
 * SudokuSolver Application
 * 
 * Main application component providing a simple prototype interface
 * for solving sudoku puzzles via the FastAPI backend.
 */

import HealthCheck from './components/HealthCheck'
import SolveForm from './components/SolveForm'
import './App.css'

function App() {
  return (
    <div className="app-container">
      {/* Header with title and health status */}
      <header style={headerStyle}>
        <h1 style={titleStyle}>SudokuSolver (Prototype)</h1>
        <HealthCheck />
      </header>

      {/* Main content area with solve form */}
      <main style={mainStyle}>
        <SolveForm />
      </main>
    </div>
  )
}

// Minimal inline styles for layout
const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '20px',
  borderBottom: '2px solid #e0e0e0',
  backgroundColor: '#f8f9fa',
}

const titleStyle: React.CSSProperties = {
  margin: 0,
  fontSize: '28px',
  color: '#333',
}

const mainStyle: React.CSSProperties = {
  padding: '40px 10px',
}

export default App
