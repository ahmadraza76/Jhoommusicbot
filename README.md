# 🎵 Telegram Music Bot

A powerful Telegram music bot that can stream music, videos, and live content in voice chats with advanced features and beautiful UI.

## ✨ Features

- 🎵 **Music Streaming**: Play music from YouTube and Spotify
- 🎥 **Video Streaming**: Stream videos in voice chats
- 📡 **Live Streaming**: Support for M3U8 live streams
- 📋 **Queue Management**: Advanced queue system with controls
- 🔐 **Authorization System**: User permission management
- 📢 **Broadcast**: Send messages to all groups
- 🎨 **Beautiful UI**: Rich inline keyboards and media responses
- ⚡ **High Performance**: Optimized for VPS deployment

## 🚀 Quick Setup

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Required
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
SUDO_USERS=user_id1,user_id2

# Optional
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
FFMPEG_PROCESSES=2
MAX_DURATION=3600
MAX_QUEUE_SIZE=50
```

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/Jhoommusicbot.git
cd Jhoommusicbot
```

2. **Install dependencies**:
```bash
chmod +x run.sh
./run.sh
```

3. **Or run manually**:
```bash
pip3 install -r requirements.txt
python3 main.py
```

### Docker Deployment

```bash
docker build -t music-bot .
docker run -d --name music-bot --env-file .env music-bot
```

## 📋 Commands

### 🎵 Playback Controls
- `/play [query|youtube_link|spotify_link]` - Stream audio
- `/vplay [query|youtube_link]` - Stream video
- `/live [m3u8_url]` - Stream live content
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/skip` - Skip to next track
- `/stop` - Stop and clear queue
- `/queue` - View current queue

### 🔐 Authorization (Private Chat)
- `/auth [user_id]` - Authorize user
- `/unauth [user_id]` - Remove authorization
- `/authusers` - List authorized users

### 📢 Broadcast (Private Chat)
- `/broadcast [message]` - Send message to all groups

## 🛠️ VPS Deployment

### Auto-Deploy with GitHub Actions

The bot includes automatic deployment to VPS. Set these GitHub secrets:

- `VPS_HOST` - Your VPS IP address
- `VPS_SSH_KEY` - Your private SSH key

### Manual VPS Setup

1. **Connect to your VPS**:
```bash
ssh root@your_vps_ip
```

2. **Clone and setup**:
```bash
git clone https://github.com/yourusername/Jhoommusicbot.git
cd Jhoommusicbot
chmod +x run.sh
./run.sh
```

3. **Run with PM2** (recommended):
```bash
npm install -g pm2
pm2 start main.py --name music-bot --interpreter python3
pm2 startup
pm2 save
```

## 🔧 Configuration

### Spotify Integration
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app and get Client ID & Secret
3. Add them to your environment variables

### Bot Setup
1. Create bot with [@BotFather](https://t.me/BotFather)
2. Get API credentials from [my.telegram.org](https://my.telegram.org)
3. Add bot to your group and make it admin
4. Grant voice chat permissions

## 📊 System Requirements

- **OS**: Ubuntu 18.04+ / Debian 9+ / CentOS 7+
- **RAM**: Minimum 512MB, Recommended 1GB+
- **CPU**: 1 vCPU minimum
- **Storage**: 1GB free space
- **Network**: Stable internet connection

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check if bot token is correct
   - Verify bot is admin in group
   - Check logs for errors

2. **Voice chat errors**:
   - Ensure bot has voice chat permissions
   - Check if voice chat is active
   - Verify FFmpeg is installed

3. **Spotify not working**:
   - Verify Spotify credentials
   - Check API limits
   - Ensure internet connectivity

### Logs

Check logs for debugging:
```bash
# If running with PM2
pm2 logs music-bot

# If running directly
python3 main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📢 **Channel**: [@MusicBotUpdates](https://t.me/MusicBotUpdates)
- 💬 **Support Group**: [@MusicBotSupport](https://t.me/MusicBotSupport)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/Jhoommusicbot/issues)

## 🌟 Features Coming Soon

- [ ] Playlist support
- [ ] Audio effects
- [ ] Multi-language support
- [ ] Web dashboard
- [ ] Database integration
- [ ] Advanced analytics

---

**Made with ❤️ by Music Bot Team**