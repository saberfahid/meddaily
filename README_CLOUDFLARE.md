# Medical Education App - Cloudflare Deployment

## 🚀 Cloudflare + GitHub Actions Setup

### 1. GitHub Repository Setup
1. Create a new GitHub repository
2. Push all files to the repository
3. Go to Settings → Secrets and variables → Actions

### 2. Add Required Secrets
```bash
OPENAI_API_KEY=l3pdbDohuqIBhQCPJWw7BkZ9QUtFRsWJ
TELEGRAM_BOT_TOKEN=8574102270:AAF_Lyi4-oLbx6isrGEPmvBSuHTPNBI56NQ
TELEGRAM_CHANNEL_ID=@medianly_sb
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token
CLOUDFLARE_ACCOUNT_ID=your-cloudflare-account-id
```

### 3. Cloudflare Pages Setup
1. Go to Cloudflare Dashboard → Pages
2. Create a new project
3. Connect to your GitHub repository
4. Set project name: `medical-edu-dashboard`
5. Build command: `echo "Building dashboard"`
6. Build output directory: `.`

### 4. What Gets Deployed

**✅ Daily Automation (GitHub Actions):**
- Runs every day at 9 AM UTC
- Generates new medical content with Mistral AI
- Creates educational videos
- Posts to Telegram @medianly_sb
- Uploads to YouTube (when quota available)

**✅ Dashboard (Cloudflare Pages):**
- Beautiful status dashboard
- Shows content statistics
- Displays recent activity
- No sensitive data exposed

### 5. Monitoring
- GitHub Actions logs: Repository → Actions tab
- Cloudflare Pages: Dashboard shows build status
- Telegram channel: @medianly_sb for content
- YouTube channel: For video uploads

### 6. Cost
- **GitHub Actions**: Free (2,000 minutes/month)
- **Cloudflare Pages**: Free
- **API Costs**: ~$5-15/month for Mistral AI

### 7. Success Indicators
✅ Daily posts in @medianly_sb  
✅ New videos on YouTube (when quota)  
✅ Dashboard showing updated stats  
✅ No workflow failures in GitHub Actions

---
*Deployment ready! Push to GitHub and watch the magic happen daily at 9 AM.*