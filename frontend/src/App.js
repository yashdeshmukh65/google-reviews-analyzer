import React, { useState } from 'react';
import { Container, Typography, Box, Paper, Grid, Button, Alert } from '@mui/material';
import FileUpload from './components/FileUpload';
import ChatSection from './components/ChatSection';
import ChartsSection from './components/ChartsSection';
import InsightsSection from './components/InsightsSection';
import './App.css';

function App() {
  const [uploadedData, setUploadedData] = useState(null);
  const [error, setError] = useState('');

  const handleNewAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:8000/clear-data', {
        method: 'POST',
      });
      
      if (response.ok) {
        setUploadedData(null);
        setError('');
      }
    } catch (err) {
      setError('Failed to clear data');
    }
  };

  return (
    <div className="App">
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h3" component="h1" gutterBottom>
            🌐 Google Reviews Analyser
          </Typography>
          {uploadedData && (
            <Button 
              variant="outlined" 
              onClick={handleNewAnalysis}
              sx={{ height: 'fit-content' }}
            >
              🆕 New Analysis
            </Button>
          )}
        </Box>

        <Typography variant="h6" color="text.secondary" gutterBottom>
          Upload your review CSV file and get AI-powered insights!
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* File Upload Section */}
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <FileUpload 
            onUploadSuccess={setUploadedData} 
            onError={setError}
            uploadedData={uploadedData}
          />
        </Paper>

        {/* Main Content - Only show if data is uploaded */}
        {uploadedData && (
          <>
            {/* Chat Section */}
            <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
              <Typography variant="h5" gutterBottom>
                🤖 Ask AI About Your Reviews
              </Typography>
              <ChatSection />
            </Paper>

            {/* Charts Section */}
            <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
              <Typography variant="h5" gutterBottom>
                📊 Review Analytics & Visualizations
              </Typography>
              <ChartsSection />
            </Paper>

            {/* Insights Section */}
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                🔮 AI Insights & Predictions
              </Typography>
              <InsightsSection />
            </Paper>
          </>
        )}
      </Container>
    </div>
  );
}

export default App;