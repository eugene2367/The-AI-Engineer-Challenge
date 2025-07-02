<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

## <h1 align="center" id="heading"> 🚀 AI Engineer Challenge - COMPLETED! 🎉</h1>

### ✨ Live Demo: [https://test-ot8mos93y-eugene-ks-projects-3278d60c.vercel.app](https://test-ot8mos93y-eugene-ks-projects-3278d60c.vercel.app)

**🎯 Mission Accomplished!** I've successfully built and deployed a beautiful, modern LLM-powered chat application that showcases the power of AI development. Here's what we've created:

## 🎨 What We Built

A **stunning, full-stack chat application** that lets you have real-time conversations with AI! Think of it as ChatGPT, but with your own custom backend and a gorgeous, modern interface.

### 🔥 Key Features
- **💬 Real-time streaming chat** - Watch AI responses appear word by word!
- **📄 Document upload & querying** - Upload files and ask questions about them!
- **🎨 Beautiful, modern UI** - Gradient backgrounds, smooth animations, and responsive design
- **⚙️ Smart configuration** - Customize system messages and manage API keys securely
- **📱 Works everywhere** - Desktop, tablet, phone - it's all responsive!
- **🔒 Built with security in mind** - Your API keys stay safe and private

## 🛠️ Tech Stack

**Frontend:**
- ⚡ **Next.js 14** - The latest and greatest React framework
- 🎯 **TypeScript** - Type-safe development for fewer bugs
- 🎨 **Tailwind CSS** - Beautiful, utility-first styling
- ✨ **Lucide React** - Gorgeous, consistent icons

**Backend:**
- 🐍 **FastAPI** - Lightning-fast Python web framework
- 🤖 **OpenAI API** - Powered by GPT-4.1-mini
- 🔄 **Streaming responses** - Real-time AI interactions
- 🧠 **Vector database** - Smart document search and retrieval

**Deployment:**
- ☁️ **Vercel** - Seamless deployment and hosting

## 🚀 How to Use

1. **Visit the app**: [https://test-ot8mos93y-eugene-ks-projects-3278d60c.vercel.app](https://test-ot8mos93y-eugene-ks-projects-3278d60c.vercel.app)
2. **Click the settings icon** (⚙️) in the top-right corner
3. **Enter your OpenAI API key** (get one from [OpenAI](https://platform.openai.com/))
4. **Optionally customize** the system message to change the AI's personality
5. **Upload a document** (text files up to 4.5MB) and ask questions about it!
6. **Start chatting!** 🎉

## 🏗️ Project Structure

```
The-AI-Engineer-Challenge/
├── 🎨 frontend/                 # Beautiful Next.js frontend
│   ├── app/                    # Next.js 14 app router
│   ├── package.json           # Dependencies and scripts
│   └── README.md              # Frontend documentation
├── 🐍 api/                     # FastAPI backend
│   ├── app.py                 # Main API server
│   └── requirements.txt       # Python dependencies
├── 🧠 aimakerspace/           # AI utilities and vector database
├── 🚀 run_api.py              # Easy API startup script
├── 🛠️ setup_dev.py            # One-click development setup
├── 🧪 test_upload.py          # Upload testing script
└── 📄 vercel.json             # Deployment configuration
```

## 🔧 Quick Development Setup

Want to run this locally? We've made it super easy! 🎉

### Option 1: One-Click Setup (Recommended)
```bash
python3 setup_dev.py
```

**🐍 Python 3.13+ Users**: If you encounter compatibility issues, use:
```bash
python3 setup_python313.py
```

### Option 2: Manual Setup
```bash
# 1. Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r api/requirements.txt

# 2. Install frontend dependencies
npm install

# 3. Start the API server
python run_api.py

# 4. Start the frontend (in a new terminal)
cd frontend
npm run dev
```

### 🧪 Testing Upload Functionality
```bash
# Test file uploads locally
python test_upload.py

# Test a specific file
python test_upload.py path/to/your/file.txt
```

## 📁 File Upload Features

### ✅ What Works
- **Text files (.txt)** up to 4.5MB
- **Real-time upload progress**
- **Smart error handling** with detailed logging
- **Document querying** - ask questions about uploaded content

### ⚠️ Current Limitations
- **PDF files**: Not supported yet (coming soon!)
- **File size**: 4.5MB limit on Vercel (10MB locally)
- **File types**: Only text files for now

### 🔍 Troubleshooting Upload Issues
If you're having trouble with file uploads, check out our detailed [Upload Troubleshooting Guide](UPLOAD_TROUBLESHOOTING.md)!

## 🎯 Challenge Completion

This project demonstrates:
- ✅ **Modern web development** with cutting-edge technologies
- ✅ **AI integration** with real-time streaming
- ✅ **Document processing** with vector search
- ✅ **Beautiful UX/UI design** with attention to detail
- ✅ **Full-stack development** from frontend to backend
- ✅ **Cloud deployment** with Vercel
- ✅ **Type safety** and best practices
- ✅ **Comprehensive error handling** and debugging tools

## 🎉 What Makes This Special

- **Real-time streaming** - No more waiting for complete responses!
- **Document intelligence** - Upload files and get smart answers!
- **Beautiful animations** - Smooth transitions and loading states
- **Responsive design** - Works perfectly on any device
- **Secure API handling** - Your keys are never stored on the server
- **Modern architecture** - Built with the latest web technologies
- **Developer-friendly** - Easy setup and comprehensive debugging tools

## 🚨 Known Issues & Solutions

### File Upload Problems?
- **5MB PDF failing?** That's Vercel's 4.5MB limit! Try a smaller file or convert to text
- **Import errors?** Make sure you're running from the root directory with `python run_api.py`
- **Need help?** Check the [troubleshooting guide](UPLOAD_TROUBLESHOOTING.md) or browser console logs

### Development Issues?
- **Module not found?** Use `python run_api.py` instead of running from the `api` directory
- **Dependencies missing?** Run `python setup_dev.py` for automatic setup
- **Python 3.13 compatibility issues?** Use `python setup_python313.py` for one-by-one installation
- **Port conflicts?** The API runs on port 8000, frontend on port 3000

---

**🌟 This is what modern AI development looks like!** 

Built with ❤️ using the latest web technologies and deployed to the cloud. The future of AI applications is here, and it's beautiful, fast, and user-friendly!

---

> **Pro tip**: This challenge shows how powerful modern development tools are when combined with AI capabilities. The result? A production-ready application that looks and feels professional! 🚀
