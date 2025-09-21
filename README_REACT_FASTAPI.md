# 🚀 Google Reviews Analyser - React + FastAPI

Modern web application with React frontend and FastAPI backend for analyzing Google Reviews with AI.

## 🏗️ **New Tech Stack**

### **Backend (FastAPI)**
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Google Gemini 1.5-Flash** - AI analysis
- **Pandas** - Data processing
- **CORS** - Cross-origin requests

### **Frontend (React)**
- **React 18** - Modern UI framework
- **Material-UI** - Professional components
- **Chart.js + React-ChartJS-2** - Interactive charts
- **React-Dropzone** - File upload
- **Axios** - API communication

## 🚀 **Setup Instructions**

### **1. Backend Setup**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs on: http://localhost:8000

### **2. Frontend Setup**
```bash
cd frontend
npm install
npm start
```
Frontend runs on: http://localhost:3000

### **3. Environment Setup**
Copy your `.env` file to the `backend` directory:
```
GEMINI_API_KEY=your_api_key_here
```

## 🎯 **Features**

### **✅ All Original Features**
- CSV file upload with drag & drop
- AI-powered question answering
- Business insights generation
- Predictive analytics
- Interactive charts and visualizations

### **🆕 New Advantages**
- **Professional UI** - Material Design components
- **Better Performance** - Separate frontend/backend
- **Scalability** - Can handle multiple users
- **Modern Architecture** - Industry standard stack
- **API Documentation** - Auto-generated at http://localhost:8000/docs

## 📊 **API Endpoints**

- `POST /upload-csv` - Upload CSV file
- `POST /ask-question` - Ask AI questions
- `GET /insights` - Get business insights
- `GET /predictions` - Get predictive analysis
- `GET /charts/*` - Get chart data
- `POST /clear-data` - Clear session data

## 🎨 **UI Components**

- **FileUpload** - Drag & drop CSV upload
- **ChatSection** - AI question interface
- **ChartsSection** - Interactive visualizations
- **InsightsSection** - AI insights display

## 🔄 **Migration Benefits**

**From Streamlit to React + FastAPI:**
- ✅ Better user experience
- ✅ Professional appearance
- ✅ Faster performance
- ✅ Mobile responsive
- ✅ Production ready
- ✅ Easier to extend

Your Google Reviews Analyser is now a modern, professional web application!