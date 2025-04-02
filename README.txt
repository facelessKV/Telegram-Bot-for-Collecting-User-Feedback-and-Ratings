⭐️ Telegram Bot Collecting User Feedback and Ratings

Want to collect not just feedback but also ratings? ⭐️⭐️⭐️⭐️⭐️
This bot helps users leave reviews and rate your service.

✅ What does it do?

• 📢 Collects text reviews
• ⭐️ Allows users to rate (from 1 to 5)
• 📊 Generates analytics based on average ratings

🔧 Features

✅ Rating system support
✅ Automatic calculation of average rating
✅ Export of feedback and ratings to a CSV file

📩 Want to improve your service with feedback and ratings?

Message me on Telegram, and I’ll help you set up this bot! 🚀

# INSTRUCTIONS FOR INSTALLING AND LAUNCHING A TELEGRAM BOT FOR REVIEWS

## WHAT DOES THE BOT DO?

This bot allows users to:
- Leave reviews of products or services
- View reviews from other users
- Rate products on a scale of 1-5 stars
- Receive statistics for administrators

## INSTALLATION ON WINDOWS

### Step 1: Install Python 3.10

1. Download Python 3.10.9 from the official website:
- Follow the link: https://www.python.org/downloads/release/python-3109/
- Scroll down to the "Files" section
- Select "Windows installer (64-bit)" to download

2. Run the downloaded file
- **IMPORTANT!** Check "Add Python 3.10 to PATH" before installing
- Click "Install Now"
- Wait for the installation to complete

3. Check the installation:
- Open a command prompt (press Win+R, enter "cmd" and press Enter)
- Enter the command: `python --version`
- The message "Python 3.10.9" (or similar version) should appear

### Step 2: Downloading and preparing the bot

1. Create a folder for the bot:
- Open Windows Explorer
- Create a new folder, for example "telegram-bot", wherever you like

2. Copy the bot files to this folder:
- File main.py
- File config.py
- File database.py
- File handlers.py
- File keyboards.py

3. Create a file .env:
- Right-click in the folder with the bot
- Select "New" -> "Text document"
- Name it ".env" (required with a period at the beginning)
- If the system does not allow you to create a file with this name, create "env.txt", and then rename it to ".env"

4. Open the .env file in Notepad and enter:
```
BOT_TOKEN=your_bot_token
ADMIN_IDS=your_numeric_id
```
(See below for information on obtaining a token and ID)

### Step 3: Installing the required libraries

1. Open a command prompt (Win+R, type "cmd", press Enter)

2. Go to the folder with the bot:
```
cd path_to_your_folder
```
For example: `cd C:\Users\Name\Desktop\telegram-bot`

3. Create a virtual environment:
```
python -m venv venv
```

4. Activate the virtual environment:
```
venv\Scripts\activate
```

5. Update pip and install the required libraries:
```
python -m pip install --upgrade pip setuptools wheel
pip install aiogram python-dotenv
```

### Step 4: Launch the bot

1. In the same command line with the environment activated:
```
python main.py
```

2. If everything is installed correctly, you will see messages about the bot initialization
3. Now you can open Telegram and find your bot

## INSTALLATION ON LINUX (Ubuntu/Debian)

### Step 1: Install Python 3.10

1. Open a terminal (Ctrl+Alt+T)

2. Update package lists:
```
sudo apt update
```

3. Install the necessary tools:
```
sudo apt install software-properties-common -y
```

4. Add a repository with Python:
```
sudo add-apt-repository ppa:deadsnakes/ppa -y
```

5. Install Python 3.10:
```
sudo apt install python3.10 python3.10-venv python3.10-dev -y
```

6. Check the installation:
```
python3.10 --version
```

### Step 2: Download and prepare the bot

1. Create a folder for the bot:
```
mkdir ~/telegram-bot
cd ~/telegram-bot
```

2. Copy the bot files to this folder:
- If the bot files are on your computer, use any available method to copy
- If the files are available via git, you can clone the repository

3. Create a .env file:
```
nano .env
```

4. Enter in the editor that opens:
```
BOT_TOKEN=your_bot_token
ADMIN_IDS=your_numeric_id
```
Save the file: Ctrl+O, then Enter, then Ctrl+X to exit

### Step 3: Installing the necessary libraries

1. While in the bot folder, create a virtual environment:
```
python3.10 -m venv venv
```

2. Activate the virtual environment:
```
source venv/bin/activate
```

3. Update pip and install the necessary libraries:
```
pip install --upgrade pip setuptools wheel
pip install aiogram python-dotenv
```

### Step 4: Launching the bot

1. In the same terminal with the activated environment:
```
python main.py
```

2. If everything is installed correctly, you will see messages about the bot initialization
3. Now you can open Telegram and find your bot

## RECEIVING A TOKEN BOT

1. Open Telegram and find @BotFather (official bot for creating bots)
2. Send the command /newbot
3. Follow the instructions:
- Enter the bot name (will be displayed in chats)
- Enter the bot username (must end with "bot")
4. BotFather will send a message with a token, it looks something like this:
`123456789:ABCdefGhIJklmNoPQRstUVwxYZ`
5. Copy this token to the .env file instead of "your_bot_token"

## GETTING ADMINISTRATOR ID

1. Find the @userinfobot bot in Telegram
2. Send it any message
3. The bot will send information about you, including your ID (numeric code)
4. Copy this ID to the .env file instead of "your_numeric_id"

## USING THE BOT

After launching the bot:

1. Find your bot in Telegram (by name, which you specified when creating)
2. Send the bot the /start command
3. Follow the bot's instructions

Available commands:
- /leave_feedback - leave a review
- /view_feedback - view reviews
- /rate - rate the product
- /stats - get statistics (for admins only)

## POSSIBLE PROBLEMS AND THEIR SOLUTIONS

### 1. "python: command not found" (Linux)
Use `python3.10` instead of `python`

### 2. "ImportError: No module named 'aiogram'"
Make sure you have activated the virtual environment before running the bot

### 3. "NameError: name 'InlineKeyboardBuilder' is not defined"
Make sure that the handlers.py file contains the import line:
```python
from aiogram.utils.keyboard import InlineKeyboardBuilder
```

### 4. "RuntimeError: This event loop is already running"
Restart the command line/terminal and try again

### 5. "Cannot connect to host api.telegram.org:443"
Check your internet connection or try via VPN

### NOTE FOR PERMANENT BOT RUNNING

These instructions only run the bot while the command line/terminal is running.
To run the bot permanently on the server, you will need to configure a system service.
