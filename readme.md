# Discord KDE Media RPC

A tool that displays your current KDE media player status as Discord Rich Presence.

NOTE: This does NOT work with Discord installed via Flatpak - use the native package or AppImage

![Discord RPC Example](https://i.postimg.cc/hGWTbvbC/rpc-2.png)
![Discord RPC Activity Example](https://i.postimg.cc/G352qzgG/rpc3.png)

## Features

- Shows currently playing media from KDE media players in your Discord status
- Automatic startup integration
- Real-time media information sync

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/gazpitchy92/discord-kde-media-rpc.git
cd discord-kde-media-rpc
```

### 2. Set Up Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Copy the **Application ID** from the General Information page
4. Open the `discord.appid` file in the project directory
5. Replace the contents with your Application ID

### 3. Set Permissions

Make the scripts executable:

```bash
chmod +x get.sh
chmod +x set.py
```

### 4. Configure Startup

To automatically start the RPC service when your system boots:

#### Using KDE Autostart Settings

1. Open **System Settings**
2. Navigate to **Startup and Shutdown** → **Autostart**
3. Click **Add...** → **Add Application**
4. Browse and select `get.sh` from the project directory
5. Click **OK**

#### Using Autostart Directory (Alternative)

1. Copy the script to your autostart directory:
   ```bash
   cp get.sh ~/.config/autostart/
   ```

#### Using Systemd (Alternative)

1. Create a systemd user service:
   ```bash
   mkdir -p ~/.config/systemd/user
   ```

2. Create a service file `~/.config/systemd/user/discord-kde-rpc.service`:
   ```ini
   [Unit]
   Description=Discord KDE Media RPC
   After=graphical-session.target

   [Service]
   Type=simple
   ExecStart=/path/to/your/discord-kde-media-rpc/get.sh
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=default.target
   ```

3. Enable and start the service:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable discord-kde-rpc.service
   systemctl --user start discord-kde-rpc.service
   ```

## Usage

### Manual Start

```bash
./get.sh
```

### Check Status

If using systemd:
```bash
systemctl --user status discord-kde-rpc.service
```

## Requirements

- KDE Plasma desktop environment
- Discord desktop application
- playerctl

## Troubleshooting

### Common Issues

**Script not starting:**
- Ensure scripts have execute permissions (`chmod +x get.sh set.py`)
- Check that Python 3 is installed and accessible

**Discord not showing status:**
- Verify your Application ID is correct in `discord.appid`
- Make sure Discord desktop app is running (web version doesn't support RPC)
- Check that your Discord privacy settings allow Rich Presence

**No media detected:**
- Ensure your media player supports MPRIS (most KDE players do)
- Try restarting the media player

**Browser media not detected:**
- Install the KDE Plasma Integration browser extension:
  - **Chrome/Chromium**: [Plasma Integration](https://chromewebstore.google.com/detail/plasma-integration/cimiefiiaegbelhefglklhhakcgmhkai)
  - **Firefox**: [Plasma Integration](https://addons.mozilla.org/en-GB/firefox/addon/plasma-integration/)
- Restart your browser after installing the extension

### Logs

Check system logs for errors:
```bash
journalctl --user -u discord-kde-rpc.service -f
```