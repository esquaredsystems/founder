---
slug: bubsy
---

Web3 communities on Telegram are a standing target for spam, scams and
coordinated FUD (fear, uncertainty and doubt) campaigns. Bubsy is an
AI-driven moderation product built for TechThree, made up of seven
repositories working together. A bot joins a community's Telegram group
and automatically detects and removes spam and bad-faith messages, bans
and mutes bad actors, and verifies new members with a captcha. Around that
core sit a shared backend, a conversational admin assistant, a
per-community Q&A persona, an AI service for image- and OCR-heavy
moderation tasks, and a web dashboard for the community's own team to see
analytics and manage members.

## Components

- **Bot**: the Telegram bot itself. Moderates groups automatically, bans
  and mutes bad actors, verifies new members with a captcha, and uses AI to
  help detect spam and bad-faith messages.
- **Backend API**: stores and manages user data, handles authentication,
  and provides the shared API that every other Bubsy service talks to.
- **Admin assistant**: turns plain-language questions into SQL queries
  against the Bubsy database, for internal or admin use.
- **Community assistant**: creates a Bubsy persona for each Web3 community
  it moderates, built from that community's own details, so it can answer
  members' questions about that specific project in Telegram.
- **AI backend**: handles the AI-heavy parts of moderation, comparing and
  analysing images, pulling text out of images with OCR, and summarising
  text.
- **Dashboard**: lets a project team connect their wallet, see analytics
  and charts about their community, manage members and subscriptions, and
  get live updates over a websocket connection.
- **Web front end**: an earlier, simpler web front end, likely superseded
  by the dashboard above.

## Stack

Node.js, Express, Telegraf, Python, FastAPI, React, Vite, Redux Toolkit,
Tailwind CSS, Redis, Kafka, PostgreSQL, MongoDB, Prisma, OpenAI, Ollama,
OpenCV, Tesseract OCR, PaddleOCR, Transformers, PyTorch, TensorFlow,
Web3.js, ethers.js, wagmi, viem, Web3Modal, ECharts, Chart.js, Socket.IO,
Docker, Jenkins, CircleCI, Swagger, Puppeteer.
