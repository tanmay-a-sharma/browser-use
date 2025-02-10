import os
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from supabase import create_client
from dotenv import load_dotenv
from typing import Dict

# Load environment variables
load_dotenv()

class CredentialManager:
	def __init__(self):
		self.supabase = create_client(
			os.getenv("SUPABASE_URL"),
			os.getenv("SUPABASE_KEY")
		)

	def get_credentials(self, website: str) -> Dict[str, str]:
		"""Get credentials for a specific website from Supabase."""
		response = self.supabase.table('auth_credentials').select("*").eq('website', website).execute()
		if not response.data:
			raise ValueError(f"No credentials found for {website}")
		credentials = response.data[0]
		return {
			"username": credentials['username'],
			"password": credentials['password']
		}

class ShoppingAssistant:
	def __init__(self):
		self.browser = Browser(
			config=BrowserConfig(
				# NOTE: you need to close your chrome browser - so that this can open your browser in debug mode
				chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
			)
		)
		self.credential_manager = CredentialManager()
		self.agent = None

	async def setup_agent(self, task: str, website: str):
		"""Initialize the agent with a specific task."""
		# Get credentials and set them as sensitive data
		credentials = self.credential_manager.get_credentials(website)
		
		# Flatten the credentials into a single level dictionary
		sensitive_data = {
			"auth_username": credentials["username"],
			"auth_password": credentials["password"],
			"website": website
		}
		
		self.agent = Agent(
			task=task,
			llm=ChatOpenAI(model='gpt-4o'),
			browser=self.browser,
			sensitive_data=sensitive_data,
			message_context="""When you need to log in:
			1. The username is stored in sensitive_data['auth_username']
			2. The password is stored in sensitive_data['auth_password']
			3. Use these credentials to log in when needed."""
		)

	async def execute_task(self, task: str, website: str):
		"""Execute a shopping task."""
		await self.setup_agent(task, website)
		if self.agent is None:
			raise ValueError("Agent was not properly initialized")
		await self.agent.run()

	async def cleanup(self):
		"""Clean up resources."""
		await self.browser.close()

async def main():
	assistant = ShoppingAssistant()
	
	# Example task that references sensitive data
	shopping_task = """Go to vuoriclothing.com and perform the following tasks:
	1. Navigate to the website (https://vuoriclothing.com)
	2. When you need to log in, use:
	   - Username from sensitive_data['auth_username']
	   - Password from sensitive_data['auth_password']
	3. Go to men's pants section
	4. Find and add a size 32 pair of pants to the cart
	
	Handle any popups or notifications that appear during the process.
	Remember: The login credentials are available in sensitive_data when you need them."""

	try:
		await assistant.execute_task(shopping_task, website='vuoriclothing.com')
	finally:
		await assistant.cleanup()
		input('Press Enter to close...')

if __name__ == '__main__':
	asyncio.run(main())
