# Confidence Booster App

A web application that generates personalized confidence-boosting essays based on your resume, helping you recognize your unique strengths and professional journey.

## Features

- Upload resumes in PDF or Word format
- Generate AI-powered confidence-boosting essays
- Clean, modern user interface
- No login required

## Prerequisites

- Docker installed on your system
- OpenAI API key

## Quick Start

1. Clone the repository:
```bash
git clone <your-repo-url>
cd confidence-booster
```

2. Create a `.env` file with your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

3. Build and run with Docker:
```bash
docker build -t confidence-booster .
docker run -p 8080:8080 --env-file .env confidence-booster
```

4. Visit `http://localhost:8080` in your browser

## Deployment Options

### Deploy to Heroku

1. Install Heroku CLI
2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Set your OpenAI API key:
```bash
heroku config:set OPENAI_API_KEY=your_api_key_here
```

5. Deploy:
```bash
git push heroku main
```

### Deploy to Railway

1. Create a new project on Railway
2. Connect your GitHub repository
3. Add your OpenAI API key as an environment variable
4. Railway will automatically build and deploy your app

### Deploy to DigitalOcean App Platform

1. Create a new app on DigitalOcean App Platform
2. Connect your GitHub repository
3. Add your OpenAI API key as an environment variable
4. Configure the app to use the Dockerfile
5. Deploy

### Deploy to Railway (Recommended)

1. Create a Railway account at [railway.app](https://railway.app)

2. Install the Railway CLI:
   ```bash
   brew install railway
   ```

3. Login to Railway:
   ```bash
   railway login
   ```

4. Create a new project:
   ```bash
   railway init
   ```

5. Add required environment variables:
   ```bash
   railway vars set OPENAI_API_KEY=your_openai_api_key
   railway vars set ADMIN_USERNAME=your_admin_username
   railway vars set ADMIN_PASSWORD=your_admin_password
   ```

6. Deploy the application:
   ```bash
   railway up
   ```

7. Your app will be deployed and available at the URL provided by Railway

Note: Railway automatically provisions a Redis instance for you, so there's no need to set up Redis separately.

## Usage Limits and Administration

The application includes built-in usage limits to prevent abuse and control costs:

- Rate limiting: 5 requests per IP address per day
- Monthly token limit: 100,000 tokens
- Automatic cleanup of usage data

### Admin Dashboard

An admin dashboard is available at `/admin` to monitor usage:
- Real-time usage statistics
- Daily request counts
- Monthly token usage trends
- Limit adjustment settings

To access the admin dashboard:
1. Set your admin credentials in environment variables:
   ```bash
   ADMIN_USERNAME=your_username
   ADMIN_PASSWORD=your_secure_password
   ```
   Default credentials (please change these):
   - Username: admin
   - Password: changeme

2. Visit `http://your-domain/admin` and enter your credentials

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional (with defaults)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme
REDIS_URL=redis://redis:6379
```

## Security Considerations

- The app doesn't store any uploaded resumes
- Files are processed in memory and immediately deleted
- CORS is enabled for web access
- Environment variables are used for sensitive data

## License

MIT License
