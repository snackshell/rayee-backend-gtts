# Deploy Ra'yee Backend to Koyeb

## Prerequisites

1. **Koyeb Account**: Sign up at https://www.koyeb.com/
2. **GitHub Account**: Your code must be in a GitHub repository
3. **Gemini API Key**: Get from https://aistudio.google.com/apikey

## Step-by-Step Deployment

### 1. Push Code to GitHub

```bash
cd backend
git init
git add .
git commit -m "Initial commit - Ra'yee Backend"
git remote add origin https://github.com/YOUR_USERNAME/rayee-backend.git
git push -u origin main
```

### 2. Deploy on Koyeb

1. **Login to Koyeb**: https://app.koyeb.com/
2. **Create New App**:
   - Click "Create App" button
   - Select "GitHub" as source

3. **Configure Repository**:
   - Connect your GitHub account
   - Select your repository
   - Select branch: `main`

4. **Configure Build**:
   - **Builder**: Buildpack
   - **Build command**: (leave empty, auto-detected)
   - **Run command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Configure Instance**:
   - **Instance type**: Nano (free tier) or Small
   - **Regions**: Choose closest to your users
   - **Scaling**: 1 instance (or more for production)

6. **Environment Variables**:
   Click "Add Variable" and add:
   ```
   Key: GEMINI_API_KEY
   Value: your_actual_gemini_api_key_here
   ```
   ⚠️ **IMPORTANT**: Keep this secret!

7. **Advanced Settings** (optional):
   - **Health check path**: `/health`
   - **Port**: 8000

8. **Deploy**:
   - Click "Deploy" button
   - Wait 2-3 minutes for deployment

### 3. Get Your Backend URL

After deployment, Koyeb will provide a URL like:
```
https://rayee-backend-YOUR-APP.koyeb.app
```

### 4. Test Your Deployment

Test the health endpoint:
```bash
curl https://rayee-backend-YOUR-APP.koyeb.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "gemini_configured": true,
  "model": "gemini-2.0-flash-exp",
  "tts_engine": "gTTS",
  "language": "Amharic (am)",
  "version": "1.0.0"
}
```

Test with an image:
```bash
curl -X POST https://rayee-backend-YOUR-APP.koyeb.app/analyze-image \
  -F "image=@test_image.jpg" \
  --output response.mp3
```

### 5. Update Flutter App

In your Flutter app settings, update the backend URL to:
```
https://rayee-backend-YOUR-APP.koyeb.app
```

## Monitoring

### View Logs

1. Go to Koyeb dashboard
2. Click on your app
3. Click "Logs" tab
4. See real-time logs

### Check Metrics

1. Go to Koyeb dashboard
2. Click on your app
3. Click "Metrics" tab
4. See CPU, memory, requests

## Troubleshooting

### "GEMINI_API_KEY environment variable not set"

- Go to Koyeb dashboard → Your App → Settings → Environment Variables
- Make sure `GEMINI_API_KEY` is set correctly
- Redeploy the app

### "Application failed to start"

- Check logs in Koyeb dashboard
- Make sure `requirements.txt` is in the repository
- Make sure `main.py` is in the repository

### "502 Bad Gateway"

- App is still starting (wait 1-2 minutes)
- Check logs for errors
- Make sure health check path is `/health`

### "Gemini returned empty response"

- Check your API key has quota remaining
- Go to https://aistudio.google.com/apikey
- Check usage limits

## Cost Estimation

**Koyeb Free Tier:**
- 1 Nano instance (512MB RAM)
- $0/month
- Perfect for testing

**Koyeb Paid:**
- Small instance (1GB RAM): ~$7/month
- Medium instance (2GB RAM): ~$14/month
- Recommended for production

## Updating Your App

When you push changes to GitHub:

```bash
git add .
git commit -m "Update backend"
git push
```

Koyeb will automatically redeploy (if auto-deploy is enabled).

Or manually redeploy:
1. Go to Koyeb dashboard
2. Click on your app
3. Click "Redeploy" button

## Security Best Practices

1. ✅ Never commit `.env` file to GitHub
2. ✅ Use environment variables for secrets
3. ✅ Keep your Gemini API key private
4. ✅ Monitor API usage regularly
5. ✅ Set up rate limiting if needed

## Alternative Deployment Options

If Koyeb doesn't work, try:

- **Render**: https://render.com/ (similar to Koyeb)
- **Railway**: https://railway.app/ (easy deployment)
- **Fly.io**: https://fly.io/ (global edge deployment)
- **Google Cloud Run**: https://cloud.google.com/run (serverless)

All use similar deployment process with `requirements.txt` and environment variables.

## Support

- Koyeb Docs: https://www.koyeb.com/docs
- Koyeb Community: https://community.koyeb.com/
- FastAPI Docs: https://fastapi.tiangolo.com/

---

**Your backend is now production-ready!** 🚀

Next step: Update your Flutter app with the Koyeb URL and test the full integration.
