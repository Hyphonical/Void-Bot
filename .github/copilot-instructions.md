# Void-Bot Copilot Instructions

## Coding Style (Strictly Enforced)

### Naming Conventions
- **Classes:** PascalCase (e.g., `Highlighter`, `RichConsole`)
- **Functions:** PascalCase (e.g., `InitLogging`, `SendMessage`)
- **Variables:** PascalCase (e.g., `ThemeDict`, `ConsoleHandler`, `UserCooldowns`)
- **Constants:** PascalCase (e.g., `BotToken`, `GuildId`)

### Import Organization
**Sort imports by length (longest to shortest) within each section:**

```python
# 📦 Built-in modules
from datetime import datetime
import logging
import asyncio

# 📥 Custom modules
from Utils.Logger import Logger
from Config import GUILD_ID
```

### Strings and Quotes
- **Always use single quotes** for strings: `'message'`, not `"message"`
- **F-strings:** Single quotes inside: `f'{variable}'`, `f'User: {name}'`
- **Exception:** Docstrings use triple double quotes: `"""Function description."""`

### Indentation
- **TABS ONLY** for indentation (no spaces)
- Each level: one tab character
- Do NOT mix tabs and spaces

### Comment Prefixes (Required)
Use emoji prefixes for section organization:
- `# 📦 Built-in modules` - Standard library imports
- `# 📥 Custom modules` - Project-specific imports
- `# 💡 [Description]` - Explanatory comments (e.g., `# 💡 Custom highlighter for log messages`)
- `# 🌱 [Section name]` - Major code sections (e.g., `# 🌱 Initialize logging`)
- `# 🧪 [Test description]` - Test code (e.g., `# 🧪 Test message sending`)

### Code Structure
- **Imports:** Built-in first (`# 📦`), then custom (`# 📥`)
- **Concise code:** Prefer clear, readable implementations
- **Emoji comments:** Use consistently for visual organization

## Example Code

```python
# 📦 Built-in modules
from datetime import datetime
import logging

# 📥 Custom modules
from Utils.Logger import Logger

# 💡 Custom class for handling messages
class MessageHandler:
	def __init__(self, Bot):
		self.Bot = Bot
		self.MessageCache = {}
	
	# 🌱 Process incoming message
	def ProcessMessage(self, Message):
		Logger.info(f'Received: {Message.content}')
		self.MessageCache[Message.id] = Message
```

Apply these rules to ALL generated or modified code.