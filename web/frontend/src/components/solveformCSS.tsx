/**
 * CSS Styles for SolveForm Component
 * 
 * Exports React.CSSProperties style objects used throughout the SolveForm component.
 */

export const containerStyle: React.CSSProperties = {
  maxWidth: '600px',
  margin: '0 auto',
  padding: '20px',
};

export const formGroupStyle: React.CSSProperties = {
  marginBottom: '16px',
};

export const labelStyle: React.CSSProperties = {
  display: 'block',
  marginBottom: '8px',
  fontWeight: 'bold',
  fontSize: '14px',
  color: '#333',
  textAlign: 'left',
};

export const radioGroupStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'row',  // Changed to row for horizontal layout
  gap: '16px',  // Increased gap for better spacing
  flexWrap: 'wrap',  // Allow wrapping on small screens
};

export const getRadioLabelStyle = (loading: boolean): React.CSSProperties => ({
  display: 'flex',
  alignItems: 'center',
  fontSize: '14px',
  color: '#333',
  cursor: loading ? 'not-allowed' : 'pointer',
});

export const getRadioInputStyle = (loading: boolean): React.CSSProperties => ({
  marginRight: '8px',
  cursor: loading ? 'not-allowed' : 'pointer',
});

export const sampleLoaderStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '8px',
  fontSize: '14px',
};

export const getSampleButtonStyle = (loading: boolean): React.CSSProperties => ({
  padding: '6px 12px',
  fontSize: '13px',
  fontWeight: '500',
  color: '#007bff',
  backgroundColor: 'white',
  border: '1px solid #007bff',
  borderRadius: '4px',
  cursor: loading ? 'not-allowed' : 'pointer',
  transition: 'all 0.2s',
});

export const getButtonStyle = (loading: boolean): React.CSSProperties => ({
  width: '100%',
  padding: '12px',
  fontSize: '16px',
  fontWeight: '600',
  color: 'white',
  backgroundColor: loading ? '#6c757d' : '#007bff',
  border: 'none',
  borderRadius: '4px',
  cursor: loading ? 'not-allowed' : 'pointer',
  transition: 'background-color 0.2s',
});

export const newPuzzleButtonStyle: React.CSSProperties = {
  width: '100%',
  padding: '12px',
  fontSize: '16px',
  fontWeight: '600',
  color: 'white',
  backgroundColor: '#28a745',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  transition: 'background-color 0.2s',
};

