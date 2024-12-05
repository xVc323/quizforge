# 🎯 QuizForge AI

> Transform any document into an intelligent quiz with the power of Google's Gemini AI

## Overview

QuizForge AI is a streamlined Streamlit application that automatically generates custom multiple-choice quizzes from your documents using Google's Gemini AI. Perfect for educators, students, and professionals who want to create engaging assessment materials quickly and efficiently.

## ✨ Features

- **📚 Support for Multiple File Formats:**
  - Documents (TXT, DOC, DOCX, PDF)
  - Code files (Python, Java, C++, HTML, etc.)
  - Spreadsheets (CSV, TSV, XLS, XLSX)

- **🎯 Customizable Quiz Generation:**
  - Multiple difficulty levels (Easy, Normal, Hard, Insane)
  - Flexible quiz lengths (5-30 questions)
  - Intelligent question generation using Gemini AI

- **📊 Rich Quiz Experience:**
  - Interactive multiple-choice interface
  - Instant scoring and feedback
  - Detailed explanations for each answer
  - Progress tracking

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

Required packages:
- streamlit
- pandas
- python-docx
- PyPDF2
- google.generativeai
- other dependencies as listed in requirements.txt

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/quizforge-ai.git
cd quizforge-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Get your Google Gemini API key:
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Create a new API key
   - Note: Free tier includes 15 API calls per minute

4. Run the application:
```bash
streamlit run app.py
```

## 🔒 Security Note

- API keys are processed securely in memory
- Never stored or logged
- Only accessible during your session
- Follow best practices for API key management

## 🎯 Usage

1. Enter your Google Gemini API key
2. Upload your documents (up to 10 files, max 100MB total)
3. Select difficulty level and number of questions
4. Generate and take the quiz
5. Review your results with detailed explanations

## 💡 Tips for Best Results

- Provide clear, well-structured documents
- Break complex topics into smaller chunks
- Use appropriate difficulty levels based on content
- Review generated questions for quality assurance

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](link-to-your-issues-page).

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Special thanks to all contributors

---
Made with ❤️ by Pat