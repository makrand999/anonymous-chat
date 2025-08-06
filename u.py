#!/usr/bin/env python3
"""
GitHub Gist Message Board Terminal App
Uses GitHub Gist API as a backend for a simple message board.
"""

import requests
import time
import json
import threading
import sys
import os
import platform
from datetime import datetime
from collections import deque

class GistMessageBoard:
    def __init__(self):
        self.gist_id = "f97354d3238ee47e8beb277eceb31cf5"
        self.filename = "gistfile1.txt"
        self.token = "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"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = f"https://api.github.com/gists/{self.gist_id}"
        self.max_messages = 45  # Clear at 45 to stay under 50
        self.running = True
        self.cache = {"content": "", "timestamp": 0}
        self.cache_duration = 1  # Cache for 1 second
        self.api_retry_count = 3
        self.api_retry_delay = 2
        self.last_request_time = 0
        self.min_request_interval = 0.5  # Rate limiting: min 0.5s between requests
        self.suppress_next_message = False

    def clear_screen(self):
        """Clear the terminal screen cross-platform."""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
    
    def clear_input_line(self):
        """Clear the current input line."""
        # Move cursor up one line and clear it
        print('\r\033[K', end='', flush=True)
    
    def display_all_messages(self, content):
        """Display all messages from content without clearing screen."""
        if content and content.strip():
            for line in content.split('\n'):
                if line.strip():
                    print(f">>{line}")
    
    def get_gist_content_with_retry(self):
        """Fetch Gist content with retry logic and caching."""
        current_time = time.time()
        
        # Check cache first
        if (current_time - self.cache["timestamp"]) < self.cache_duration:
            return self.cache["content"]
        
        # Rate limiting
        if (current_time - self.last_request_time) < self.min_request_interval:
            time.sleep(self.min_request_interval - (current_time - self.last_request_time))
        
        for attempt in range(self.api_retry_count):
            try:
                self.last_request_time = time.time()
                response = requests.get(self.base_url, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                gist_data = response.json()
                content = ""
                if self.filename in gist_data['files']:
                    content = gist_data['files'][self.filename]['content']
                
                # Update cache
                self.cache = {"content": content, "timestamp": current_time}
                return content
                
            except requests.RequestException as e:
                if attempt < self.api_retry_count - 1:
                    print(f">>Connection error, retrying in {self.api_retry_delay}s... ({attempt + 1}/{self.api_retry_count})")
                    time.sleep(self.api_retry_delay)
                else:
                    print(">>Connection failed. Working offline until reconnected.")
                    return None
        
        return None
    
    def update_gist_content_with_retry(self, new_content):
        """Update Gist content with retry logic and rate limiting."""
        current_time = time.time()
        
        # Rate limiting
        if (current_time - self.last_request_time) < self.min_request_interval:
            time.sleep(self.min_request_interval - (current_time - self.last_request_time))
        
        for attempt in range(self.api_retry_count):
            try:
                data = {
                    "files": {
                        self.filename: {
                            "content": new_content
                        }
                    }
                }
                
                self.last_request_time = time.time()
                response = requests.patch(self.base_url, 
                                        headers=self.headers, 
                                        data=json.dumps(data),
                                        timeout=10)
                response.raise_for_status()
                
                # Update cache
                self.cache = {"content": new_content, "timestamp": current_time}
                return True
                
            except requests.RequestException as e:
                if attempt < self.api_retry_count - 1:
                    time.sleep(self.api_retry_delay)
                else:
                    print(">>Failed to send message. Please try again.")
                    return False
        
        return False
    
    def count_messages(self, content):
        """Count the number of messages in the content."""
        if not content or not content.strip():
            return 0
        return len([line for line in content.split('\n') if line.strip()])
    
    def auto_clear_if_needed(self, current_content):
        """Auto-clear Gist when message limit is reached."""
        message_count = self.count_messages(current_content)
        if message_count >= self.max_messages:
            print(f">>Message limit reached ({self.max_messages}). Auto-clearing...")
            if self.update_gist_content_with_retry(""):
                self.cache = {"content": "", "timestamp": time.time()}
                print(">>Board cleared. Starting fresh!")
                return True
            else:
                print(">>Failed to clear board.")
                return False
        return False
    
    def add_message(self, message):
        """Add a new message to the Gist."""
        # Clear the input line first
        self.clear_input_line()
        
        current_content = self.get_gist_content_with_retry()
        if current_content is None:
            return False
        
        # Check if auto-clear is needed before adding
        if self.auto_clear_if_needed(current_content):
            current_content = ""
        
        # Add the new message
        if current_content.strip():
            new_content = current_content + "\n" + message
        else:
            new_content = message
        
        success = self.update_gist_content_with_retry(new_content)
        if success:
            self.suppress_next_message = True  # Suppress the next new message

        return success
    
    def monitor_messages(self):
        """Background thread to monitor for new messages."""
        last_content = ""
        while self.running:
            try:
                current_content = self.get_gist_content_with_retry()
                if current_content is not None and current_content != last_content:
                    # Clear the input line and display new messages
                    self.clear_input_line()
                    
                    # Find and display only new messages
                    if last_content == "":
                        # First load - display all messages
                        self.display_all_messages(current_content)
                    else:
                        # Find new messages
                        last_lines = last_content.split('\n') if last_content else []
                        current_lines = current_content.split('\n') if current_content else []
                        
                        if len(current_lines) > len(last_lines):
                            new_lines = current_lines[len(last_lines):]
                            if self.suppress_next_message:
                                # Skip the first new message
                                new_lines = new_lines[1:]
                                self.suppress_next_message = False  # Reset flag
                            for line in new_lines:
                                if line.strip():
                                    print(f">>{line}")

                    
                    last_content = current_content
                time.sleep(2)
            except Exception as e:
                # Silently continue on errors to maintain stability
                time.sleep(5)  # Wait longer on unexpected errors
    
    def get_cross_platform_input(self, prompt):
        """Cross-platform input handling."""
        try:
            if platform.system() == "Windows":
                # Windows compatible input
                return input(prompt).strip()
            else:
                # Unix-like systems
                return input(prompt).strip()
        except EOFError:
            return "quit"
        except KeyboardInterrupt:
            return "quit"
    
    def show_help(self):
        """Show available commands."""
        print(">>Commands:")
        print(">>  clear - Refresh display")
        print(">>  count - Show message count")
        print(">>  reset - Clear all messages from board")
        print(">>  help - Show this help")
        print(">>  quit - Exit application")
    
    def handle_command(self, command):
        """Handle special commands."""
        cmd = command.lower().strip()
        
        if cmd == "clear":
            current_content = self.get_gist_content_with_retry()
            if current_content is not None:
                self.display_all_messages(current_content)
            return True
            
        elif cmd == "count":
            current_content = self.get_gist_content_with_retry()
            if current_content is not None:
                count = self.count_messages(current_content)
                print(f">>Messages: {count}/{self.max_messages}")
            else:
                print(">>Cannot get message count (offline)")
            return True
            
        elif cmd == "reset":
            print(">>Clearing all messages...")
            if self.update_gist_content_with_retry(""):
                self.display_all_messages("")
                print(">>Board cleared!")
            else:
                print(">>Failed to clear board.")
            return True
            
        elif cmd == "help":
            self.show_help()
            return True
            
        elif cmd in ["quit", "exit", "q"]:
            return "quit"
        
        return False
    
    def run(self):
        """Main application loop."""
        # Load initial content and display existing messages
        print(">>Connecting...")
        initial_content = self.get_gist_content_with_retry()
        if initial_content is None:
            print(">>Working offline. Messages will sync when reconnected.")
            initial_content = ""
        else:
            print(">>Connected!")
        
        # Display existing messages
        self.display_all_messages(initial_content)
        
        # Show initial count
        if initial_content is not None:
            count = self.count_messages(initial_content)
            if count > 0:
                print(f">>Messages: {count}/{self.max_messages}")
        
        # Start background monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_messages, daemon=True)
        monitor_thread.start()
        
        try:
            while True:
                user_input = self.get_cross_platform_input(">>")
                
                if not user_input:
                    continue
                
                # Handle commands
                cmd_result = self.handle_command(user_input)
                if cmd_result == "quit":
                    break
                elif cmd_result:
                    continue
                
                # Regular message
                if len(user_input) <= 50:
                    self.add_message(user_input)
                else:
                    print(">>Message too long (max 50 chars)")
                
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            print(">>Goodbye!")

def main():
    """Entry point of the application."""
    try:
        board = GistMessageBoard()
        board.run()
    except Exception as e:
        print(f">>Fatal error: {e}")

if __name__ == "__main__":
    main()