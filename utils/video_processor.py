import os
import subprocess
import tempfile
from pathlib import Path
import ffmpeg
from moviepy.editor import VideoFileClip

class VideoProcessor:
    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def extract_thumbnail(self, video_path, output_path, time='00:00:01'):
        """Extract thumbnail from video at specific time"""
        try:
            (
                ffmpeg
                .input(video_path, ss=time)
                .output(output_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error extracting thumbnail: {e}")
            return False
    
    async def extract_multiple_thumbnails(self, video_path, output_dir, intervals=5):
        """Extract multiple thumbnails at regular intervals"""
        try:
            # Get video duration
            probe = ffmpeg.probe(video_path)
            duration = float(probe['streams'][0]['duration'])
            
            interval = duration / intervals
            
            thumbnails = []
            for i in range(intervals):
                time = i * interval
                output_file = os.path.join(output_dir, f"thumb_{i+1}.jpg")
                
                (
                    ffmpeg
                    .input(video_path, ss=time)
                    .output(output_file, vframes=1)
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                thumbnails.append(output_file)
            
            return thumbnails
        except Exception as e:
            print(f"Error extracting multiple thumbnails: {e}")
            return []
    
    async def trim_video(self, video_path, output_path, start_time, end_time):
        """Trim video from start_time to end_time"""
        try:
            (
                ffmpeg
                .input(video_path, ss=start_time, to=end_time)
                .output(output_path)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error trimming video: {e}")
            return False
    
    async def merge_videos(self, video_paths, output_path):
        """Merge multiple videos"""
        try:
            # Create concat file
            concat_file = os.path.join(self.temp_dir, "concat.txt")
            with open(concat_file, 'w') as f:
                for path in video_paths:
                    f.write(f"file '{os.path.abspath(path)}'\n")
            
            (
                ffmpeg
                .input(concat_file, format='concat', safe=0)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return True
        except Exception as e:
            print(f"Error merging videos: {e}")
            return False
    
    async def split_video_by_time(self, video_path, output_dir, segment_duration):
        """Split video into segments by time duration"""
        try:
            output_pattern = os.path.join(output_dir, "segment_%03d.mp4")
            
            (
                ffmpeg
                .input(video_path)
                .output(output_pattern, **{
                    'c': 'copy',
                    'f': 'segment',
                    'segment_time': segment_duration,
                    'reset_timestamps': '1'
                })
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # Get list of created segments
            segments = sorted([f for f in os.listdir(output_dir) if f.startswith('segment_')])
            return [os.path.join(output_dir, seg) for seg in segments]
        except Exception as e:
            print(f"Error splitting video: {e}")
            return []
    
    async def optimize_video(self, video_path, output_path, preset='balanced'):
        """Optimize video for smaller size"""
        presets = {
            'high': {'crf': 18, 'preset': 'slow'},
            'balanced': {'crf': 23, 'preset': 'medium'},
            'small': {'crf': 28, 'preset': 'fast'}
        }
        
        config = presets.get(preset, presets['balanced'])
        
        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, **{
                    'c:v': 'libx264',
                    'crf': config['crf'],
                    'preset': config['preset'],
                    'c:a': 'aac',
                    'b:a': '128k'
                })
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error optimizing video: {e}")
            return False
    
    async def add_subtitles(self, video_path, subtitle_path, output_path, burn=True):
        """Add subtitles to video"""
        try:
            if burn:
                # Burn subtitles into video
                (
                    ffmpeg
                    .input(video_path)
                    .output(output_path, vf=f"subtitles={subtitle_path}")
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
            else:
                # Soft subtitles
                (
                    ffmpeg
                    .input(video_path)
                    .output(output_path, c='copy')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
            return True
        except Exception as e:
            print(f"Error adding subtitles: {e}")
            return False
    
    async def take_screenshots(self, video_path, output_dir, times=None, interval=None):
        """Take screenshots at specific times or intervals"""
        try:
            if times:
                screenshots = []
                for i, time in enumerate(times):
                    output_file = os.path.join(output_dir, f"screenshot_{i+1}.jpg")
                    (
                        ffmpeg
                        .input(video_path, ss=time)
                        .output(output_file, vframes=1)
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                    screenshots.append(output_file)
                return screenshots
            
            elif interval:
                # Get video duration
                probe = ffmpeg.probe(video_path)
                duration = float(probe['streams'][0]['duration'])
                
                screenshots = []
                count = int(duration / interval)
                
                for i in range(count):
                    time = i * interval
                    output_file = os.path.join(output_dir, f"screenshot_{i+1}.jpg")
                    (
                        ffmpeg
                        .input(video_path, ss=time)
                        .output(output_file, vframes=1)
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                    screenshots.append(output_file)
                
                return screenshots
            
            else:
                # Single screenshot at middle
                probe = ffmpeg.probe(video_path)
                duration = float(probe['streams'][0]['duration'])
                middle = duration / 2
                
                output_file = os.path.join(output_dir, "screenshot.jpg")
                (
                    ffmpeg
                    .input(video_path, ss=middle)
                    .output(output_file, vframes=1)
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
                return [output_file]
                
        except Exception as e:
            print(f"Error taking screenshots: {e}")
            return []

# Global instance
video_processor = VideoProcessor()

# Convenience functions
async def extract_thumbnail(*args, **kwargs):
    return await video_processor.extract_thumbnail(*args, **kwargs)

async def trim_video(*args, **kwargs):
    return await video_processor.trim_video(*args, **kwargs)

async def merge_videos(*args, **kwargs):
    return await video_processor.merge_videos(*args, **kwargs)

async def split_video(*args, **kwargs):
    return await video_processor.split_video_by_time(*args, **kwargs)

async def optimize_video(*args, **kwargs):
    return await video_processor.optimize_video(*args, **kwargs)

async def add_subtitles(*args, **kwargs):
    return await video_processor.add_subtitles(*args, **kwargs)

async def take_screenshots(*args, **kwargs):
    return await video_processor.take_screenshots(*args, **kwargs)
