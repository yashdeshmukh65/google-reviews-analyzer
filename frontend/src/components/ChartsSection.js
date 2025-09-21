import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ChartsSection = () => {
  const [ratingData, setRatingData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);

  useEffect(() => {
    fetchChartData();
  }, []);

  const fetchChartData = async () => {
    try {
      // Fetch rating distribution
      const ratingResponse = await fetch('http://localhost:8000/charts/rating-distribution');
      const ratingResult = await ratingResponse.json();
      
      if (ratingResult.success) {
        setRatingData({
          labels: ratingResult.data.labels.map(label => `${label} Stars`),
          datasets: [{
            label: 'Number of Reviews',
            data: ratingResult.data.values,
            backgroundColor: [
              '#ff6b6b',
              '#ffa726',
              '#ffeb3b',
              '#66bb6a',
              '#4caf50'
            ],
            borderColor: [
              '#f44336',
              '#ff9800',
              '#ffeb3b',
              '#4caf50',
              '#2e7d32'
            ],
            borderWidth: 1
          }]
        });
      }

      // Fetch sentiment pie
      const sentimentResponse = await fetch('http://localhost:8000/charts/sentiment-pie');
      const sentimentResult = await sentimentResponse.json();
      
      if (sentimentResult.success) {
        setSentimentData({
          labels: sentimentResult.data.labels,
          datasets: [{
            data: sentimentResult.data.values,
            backgroundColor: [
              '#4caf50',
              '#8bc34a',
              '#ffeb3b',
              '#ff9800',
              '#f44336'
            ],
            borderColor: [
              '#2e7d32',
              '#689f38',
              '#f57f17',
              '#e65100',
              '#c62828'
            ],
            borderWidth: 2
          }]
        });
      }
    } catch (error) {
      console.error('Error fetching chart data:', error);
    }
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
      },
    },
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={2} sx={{ p: 2, height: 400 }}>
          <Typography variant="h6" gutterBottom>
            Rating Distribution
          </Typography>
          <Box sx={{ height: 320 }}>
            {ratingData ? (
              <Bar data={ratingData} options={chartOptions} />
            ) : (
              <Typography>Loading chart...</Typography>
            )}
          </Box>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper elevation={2} sx={{ p: 2, height: 400 }}>
          <Typography variant="h6" gutterBottom>
            Sentiment Analysis
          </Typography>
          <Box sx={{ height: 320 }}>
            {sentimentData ? (
              <Pie data={sentimentData} options={pieOptions} />
            ) : (
              <Typography>Loading chart...</Typography>
            )}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default ChartsSection;