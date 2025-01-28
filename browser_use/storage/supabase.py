from __future__ import annotations

import base64
import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from supabase import Client, create_client
from storage3.exceptions import StorageApiError

logger = logging.getLogger(__name__)
load_dotenv()

class SupabaseStorage:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client: Client = create_client(supabase_url, supabase_key)
        self.bucket_name = "screenshots"
        
        # List all buckets to check if ours exists
        try:
            buckets = self.client.storage.list_buckets()
            bucket_exists = any(b['name'] == self.bucket_name for b in buckets)
            
            if not bucket_exists:
                try:
                    self.client.storage.create_bucket(
                        self.bucket_name,
                        options={'public': True}
                    )
                    logger.info(f"Created new bucket: {self.bucket_name}")
                except StorageApiError as e:
                    logger.warning(f"Could not create bucket, will attempt to use existing: {str(e)}")
            else:
                logger.info(f"Using existing bucket: {self.bucket_name}")
                
        except Exception as e:
            logger.error(f"Error setting up storage bucket: {str(e)}")
            raise

    def save_screenshot(self, agent_id: str, step_num: int, screenshot_data: bytes) -> str:
        """
        Save a screenshot to Supabase Storage.
        
        Args:
            agent_id: Unique identifier for the agent
            step_num: Step number for the screenshot
            screenshot_data: Raw screenshot data
            
        Returns:
            URL of the saved screenshot
        """
        file_path = f"{agent_id}/step_{step_num}_screenshot.png"
        
        try:
            # First try to delete if exists (to handle updates)
            try:
                self.client.storage.from_(self.bucket_name).remove([file_path])
            except:
                pass
                
            # Upload the new file
            self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=screenshot_data,
                file_options={"contentType": "image/png"}
            )
            
            # Get public URL
            url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            logger.info(f"Saved screenshot to: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to save screenshot to Supabase: {str(e)}")
            raise

    def get_screenshot_url(self, agent_id: str, step_num: int) -> Optional[str]:
        """Get the public URL for a screenshot if it exists."""
        file_path = f"{agent_id}/step_{step_num}_screenshot.png"
        try:
            return self.client.storage.from_(self.bucket_name).get_public_url(file_path)
        except:
            return None
