# 🎨 Sourcely Frontend

React + Vite interface for interacting with the Sourcely research assistant.

## 🚀 Setup

1. **install dependencies**:

   ```bash
   npm install
   ```

2. **run development server**:

   ```bash
   npm run dev
   ```

3. **access the app**:

   Open [http://localhost:5173](http://localhost:5173) in your browser.

## 🛠️ tech stack

- **react 19**: modern ui library.
- **vite**: ultra-fast build tool.
- **tailwind css**: utility-first styling.
- **axios**: backend communication.

## 📁 Project Structure

```text
frontend/
├── public/              # static assets
├── src/
│   ├── api/            # axios client & api calls
│   ├── assets/         # images & styles
│   ├── components/     # reusable ui components
│   │   ├── AnswerDisplay.jsx
│   │   ├── ChatInput.jsx
│   │   ├── FileUpload.jsx
│   │   └── StatusBar.jsx
│   ├── App.jsx         # main application state & layout
│   ├── index.css       # global styles
│   └── main.jsx        # react entry point
├── index.html          # html template
├── package.json        # dependencies & scripts
└── vite.config.js      # vite configuration
```
