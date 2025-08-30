# 📦 Built-in modules
import os

# 📥 Custom modules
from Utils.Logger import Logger


# 🌱 Load environment variables from .env file
def LoadEnv():
	EnvDict = {}
	try:
		with open('.env', 'r') as File:
			for Line in File:
				if '=' in Line:
					Key, Value = Line.strip().split('=', 1)
					EnvDict[Key] = Value
					os.environ[Key] = Value
		return EnvDict
	except FileNotFoundError:
		# 🔄 Fallback to process environment when .env is missing
		Keys = [
			'DISCORD_BOT_TOKEN',
			'PLAN_USER',
			'PLAN_PASSWORD',
			'PLAN_SERVER_UUID',
		]
		for Key in Keys:
			Value = os.environ.get(Key)
			if Value:
				EnvDict[Key] = Value
		if not EnvDict:
			Logger.error('Error: .env file not found and no environment variables set.')
			return {}
		return EnvDict
