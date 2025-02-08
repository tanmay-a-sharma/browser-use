import os
import sys
from pathlib import Path
from browser_use.agent.views import ActionResult
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from langchain_openai import ChatOpenAI
from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
	os.getenv("SUPABASE_URL"),
	os.getenv("SUPABASE_KEY")
)

# Get credentials from Supabase
def get_credentials():
	response = supabase.table('auth_credentials').select("*").eq('website', 'vuoriclothing.com').execute()
	if not response.data:
		raise ValueError("No credentials found for vuoriclothing.com")
	credentials = response.data[0]
	return credentials['username'], credentials['password']

# Setup browser
browser = Browser(
	config=BrowserConfig(
		# NOTE: you need to close your chrome browser - so that this can open your browser in debug mode
		chrome_instance_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
	)
)

async def main():
	# Get credentials
	username, password = get_credentials()
	
	# Create the shopping task
	vuori_task = f"""Go to vuoriclothing.com and perform the following tasks:
	1. Navigate to the website (https://vuoriclothing.com)
	2. Log in using these credentials:
	   - Username/Email: {username}
	   - Password: {password}
	3. Go to men's pants section
	4. Find and add a pair of pants to the cart
	
	Handle any popups or notifications that appear during the process.
	Make sure to complete the login process before proceeding to shopping."""

	agent = Agent(
		task=vuori_task,
		llm=ChatOpenAI(model='gpt-4o'),
		browser=browser,
	)

	await agent.run()
	await browser.close()

	input('Press Enter to close...')

if __name__ == '__main__':
	asyncio.run(main())
