import React, { useState } from 'react';
import { Box, Button, Typography, Paper, Grid, CircularProgress } from '@mui/material';
import { Psychology, TrendingUp, Visibility } from '@mui/icons-material';

const InsightsSection = () => {
  const [insights, setInsights] = useState('');
  const [predictions, setPredictions] = useState('');
  const [loading, setLoading] = useState({ insights: false, predictions: false });

  const getInsights = async () => {
    setLoading(prev => ({ ...prev, insights: true }));
    
    try {
      const response = await fetch('http://localhost:8000/insights');
      const result = await response.json();
      
      if (result.success) {
        setInsights(result.insights);
      } else {
        setInsights('Failed to generate insights');
      }
    } catch (error) {
      setInsights('Error connecting to server');
    }
    
    setLoading(prev => ({ ...prev, insights: false }));
  };

  const getPredictions = async () => {
    setLoading(prev => ({ ...prev, predictions: true }));
    
    try {
      const response = await fetch('http://localhost:8000/predictions');
      const result = await response.json();
      
      if (result.success) {
        setPredictions(result.predictions);
      } else {
        setPredictions('Failed to generate predictions');
      }
    } catch (error) {
      setPredictions('Error connecting to server');
    }
    
    setLoading(prev => ({ ...prev, predictions: false }));
  };

  return (
    <Box>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6}>
          <Button
            variant="contained"
            startIcon={loading.insights ? <CircularProgress size={20} /> : <Psychology />}
            onClick={getInsights}
            disabled={loading.insights}
            fullWidth
            sx={{ py: 1.5 }}
          >
            {loading.insights ? 'Generating...' : 'Get AI Insights'}
          </Button>
        </Grid>
        
        <Grid item xs={12} sm={6}>
          <Button
            variant="contained"
            startIcon={loading.predictions ? <CircularProgress size={20} /> : <TrendingUp />}
            onClick={getPredictions}
            disabled={loading.predictions}
            fullWidth
            sx={{ py: 1.5 }}
          >
            {loading.predictions ? 'Predicting...' : 'Predictive Analysis'}
          </Button>
        </Grid>
      </Grid>

      {insights && (
        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Psychology /> AI Business Insights
          </Typography>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
            {insights}
          </Typography>
        </Paper>
      )}

      {predictions && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUp /> Predictive Analysis
          </Typography>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
            {predictions}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default InsightsSection;