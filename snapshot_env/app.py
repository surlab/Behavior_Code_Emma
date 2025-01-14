import numpy as np
import cv2
import pyautogui
from PIL import Image
import os
import threading
from queue import Queue
import time
from tkinter import Tk, messagebox

print("Starting app...")

def get_screen_resolution():
    """Get current screen resolution"""
    print("Getting screen resolution...")
    screen_width, screen_height = pyautogui.size()
    print(f"Screen size: {screen_width}x{screen_height}")
    return screen_width, screen_height

def preview_region(region):
    """Show preview of selected region"""
    print(f"Previewing region: {region}")
    try:
        preview = pyautogui.screenshot(region=region)
        preview_np = np.array(preview)
        preview_np = cv2.cvtColor(preview_np, cv2.COLOR_RGB2BGR)
        
        cv2.imshow('Preview (Press SPACE to accept, ESC to retry)', preview_np)
        key = cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()
        
        return key == 32
    except Exception as e:
        print(f"Error in preview_region: {e}")
        return False

def get_region_by_clicks():
    """Get region coordinates using mouse clicks"""
    print("Starting region selection...")
    try:
        messagebox.showinfo("Instructions", 
                           "You will now select the recording region:\n"
                           "1. Move cursor to TOP LEFT corner and press OK\n"
                           "2. Move cursor to BOTTOM RIGHT corner and press OK")
        
        screen_width, screen_height = get_screen_resolution()
        
        while True:
            print("Waiting for top-left corner selection...")
            messagebox.showinfo("Select Region", "Move cursor to TOP LEFT corner and press OK")
            x1, y1 = pyautogui.position()
            print(f"Top-left corner selected: ({x1}, {y1})")
            
            print("Waiting for bottom-right corner selection...")
            messagebox.showinfo("Select Region", "Move cursor to BOTTOM RIGHT corner and press OK")
            x2, y2 = pyautogui.position()
            print(f"Bottom-right corner selected: ({x2}, {y2})")
            
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            width = x2 - x1
            height = y2 - y1
            
            print(f"Selected region: {width}x{height} pixels")
            
            if width < 10 or height < 10:
                print("Error: Region too small")
                messagebox.showerror("Error", "Selected region is too small!")
                continue
            
            if x2 > screen_width or y2 > screen_height:
                print("Error: Region outside screen bounds")
                messagebox.showerror("Error", "Selected region is outside screen bounds!")
                continue
            
            region = (x1, y1, width, height)
            print(f"Final region: {region}")
            
            if preview_region(region):
                return region
    except Exception as e:
        print(f"Error in get_region_by_clicks: {e}")
        raise

def screen_recorder(region, output_queue, stop_event):
    print("Starting screen recorder...")
    try:
        while not stop_event.is_set():
            frame = pyautogui.screenshot(region=region)
            frame = np.array(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            output_queue.put(frame)
            time.sleep(0.033)
    except Exception as e:
        print(f"Error in screen_recorder: {e}")
        stop_event.set()

def process_frame(frame):
    try:
        processed = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return processed
    except Exception as e:
        print(f"Error in process_frame: {e}")
        return frame

def main():
    print("Starting main function...")
    try:
        region = get_region_by_clicks()
        print(f"Region selected: {region}")
        
        frame_queue = Queue(maxsize=30)
        stop_event = threading.Event()
        
        recorder_thread = threading.Thread(
            target=screen_recorder,
            args=(region, frame_queue, stop_event)
        )
        recorder_thread.start()
        print("Recording thread started")
        
        try:
            while True:
                if not frame_queue.empty():
                    frame = frame_queue.get()
                    processed_frame = process_frame(frame)
                    
                    cv2.imshow('Original', frame)
                    cv2.imshow('Processed', processed_frame)
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Quit signal received")
                        break
        
        finally:
            print("Cleaning up...")
            stop_event.set()
            recorder_thread.join()
            cv2.destroyAllWindows()
            
    except Exception as e:
        print(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    print("Script started")
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        input("Press Enter to exit...")  # Keep window open to see error 