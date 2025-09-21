import React, { useState } from 'react';
import { Box, TextField, Button, Grid, Chip, Typography, Paper, CircularProgress } from '@mui/material';
import { Send } from '@mui/icons-material';

const ChatSection = () => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sampleQuestions = [
    "What are the main complaints?",
    "What do customers love most?",
    "How can we improve ratings?",
    "What are common positive themes?",
    "What issues appear most frequently?",
    "Give me actionable recommendations"
  ];

  const askQuestion = async (questionText) => {
    if (!questionText.trim()) return;

    setLoading(true);
    setMessages(prev => [...prev, { type: 'user', text: questionText }]);

    try {
      const response = await fetch('http://localhost:8000/ask-question', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: questionText }),
      });

      const result = await response.json();
      
      if (result.success) {
        setMessages(prev => [...prev, { type: 'ai', text: result.response }]);
      } else {
        setMessages(prev => [...prev, { type: 'ai', text: 'Sorry, I encountered an error processing your question.' }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { type: 'ai', text: 'Error: Could not connect to the server.' }]);
    }

    setLoading(false);
    setQuestion('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    askQuestion(question);
  };

  return (
    <Box>
      {/* Sample Questions */}
      <Typography variant="h6" gutterBottom>
        💡 Quick Questions:
      </Typography>
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={1}>
          {sampleQuestions.map((q, index) => (
            <Grid item key={index}>
              <Chip
                label={q}
                onClick={() => askQuestion(q)}
                variant="outlined"
                sx={{ cursor: 'pointer' }}
              />
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Chat Messages */}
      {messages.length > 0 && (
        <Paper 
          elevation={1} 
          sx={{ 
            maxHeight: 400, 
            overflow: 'auto', 
            p: 2, 
            mb: 2,
            backgroundColor: '#fafafa'
          }}
        >
          {messages.map((message, index) => (
            <Box
              key={index}
              sx={{
                mb: 2,
                p: 2,
                borderRadius: 2,
                backgroundColor: message.type === 'user' ? '#e3f2fd' : '#f5f5f5',
                textAlign: message.type === 'user' ? 'right' : 'left',
              }}
            >
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {message.text}
              </Typography>
            </Box>
          ))}
          {loading && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={20} />
              <Typography variant="body2" color="text.secondary">
                AI is analyzing your reviews...
              </Typography>
            </Box>
          )}
        </Paper>
      )}

      {/* Question Input */}
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask anything about your reviews..."
            variant="outlined"
          />
          <Button
            type="submit"
            variant="contained"
            endIcon={<Send />}
            disabled={loading || !question.trim()}
            sx={{ minWidth: 120 }}
          >
            Ask AI
          </Button>
        </Box>
      </form>
    </Box>
  );
};

export default ChatSection;