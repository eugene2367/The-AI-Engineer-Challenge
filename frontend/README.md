# AI Engineer Challenge Frontend

A modern, responsive chat application built with Next.js, TypeScript, and Tailwind CSS that integrates with the FastAPI backend.

## Features

- 🎨 Beautiful, modern UI with gradient backgrounds and smooth animations
- 💬 Real-time streaming chat with OpenAI's GPT-4.1-mini model
- ⚙️ Configurable system messages and API key management
- 📱 Fully responsive design that works on all devices
- 🔒 Secure API key handling (never stored on server)
- ⚡ Fast performance with Next.js 14

## Getting Started

### Prerequisites

- Node.js 18+ installed
- OpenAI API key

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

1. Build the application:
   ```bash
   npm run build
   ```

2. Start the production server:
   ```bash
   npm start
   ```

## Usage

1. Click the settings icon (⚙️) in the top-right corner
2. Enter your OpenAI API key in the settings panel
3. Optionally customize the system message
4. Start chatting with the AI!

## Architecture

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **FastAPI Backend**: Python backend for AI processing

## API Integration

The frontend communicates with the FastAPI backend at `/api/chat` endpoint, sending:
- `developer_message`: System prompt
- `user_message`: User input
- `model`: AI model (gpt-4.1-mini)
- `api_key`: OpenAI API key

The response is streamed in real-time for a smooth user experience.