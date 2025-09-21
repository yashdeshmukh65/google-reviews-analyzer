import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Button, Grid, Card, CardContent } from '@mui/material';
import { CloudUpload, GetApp } from '@mui/icons-material';

const FileUpload = ({ onUploadSuccess, onError, uploadedData }) => {
  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload-csv', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (result.success) {
        onUploadSuccess(result.data);
        onError('');
      } else {
        onError('Failed to upload file');
      }
    } catch (err) {
      onError('Error uploading file: ' + err.message);
    }
  }, [onUploadSuccess, onError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    multiple: false
  });

  const downloadSample = () => {
    const sampleData = `title,url,stars,text
Pizza Palace,https://maps.google.com/pizza-palace,5,"Amazing pizza! Best in town!"
Pizza Palace,https://maps.google.com/pizza-palace,4,"Good food but slow service"
Pizza Palace,https://maps.google.com/pizza-palace,3,"Average experience"`;
    
    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_reviews.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Box
          {...getRootProps()}
          className={`upload-area ${isDragActive ? 'active' : ''}`}
          sx={{
            border: '2px dashed #ccc',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            '&:hover': {
              borderColor: 'primary.main',
            }
          }}
        >
          <input {...getInputProps()} />
          <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop the CSV file here' : 'Drag & drop CSV file here, or click to select'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Required columns: title, url, stars, text
          </Typography>
        </Box>
      </Grid>
      
      <Grid item xs={12} md={4}>
        <Button
          variant="outlined"
          startIcon={<GetApp />}
          onClick={downloadSample}
          fullWidth
          sx={{ mb: 2 }}
        >
          Download Sample CSV
        </Button>
        
        {uploadedData && (
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main" gutterBottom>
                ✅ Data Loaded Successfully!
              </Typography>
              <Typography variant="body2">
                <strong>Business:</strong> {uploadedData.business_name}
              </Typography>
              <Typography variant="body2">
                <strong>Reviews:</strong> {uploadedData.total_reviews}
              </Typography>
              <Typography variant="body2">
                <strong>Avg Rating:</strong> {uploadedData.avg_rating}⭐
              </Typography>
            </CardContent>
          </Card>
        )}
      </Grid>
    </Grid>
  );
};

export default FileUpload;