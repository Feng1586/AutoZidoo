import os
import datetime
import logs

def create_media_structure(base_dir="/mnt/zidoo"):
    media_dir = os.path.join(base_dir, "media")
    downloads_dir = os.path.join(media_dir, "downloads")
    movies_dir = os.path.join(media_dir, "movies")
    tv_dir = os.path.join(media_dir, "tv")
    
    # 检查是否存在 /mnt/zidoo/media 目录
    if not os.path.exists(media_dir):
        try:
            # 创建 /mnt/zidoo/media 目录
            os.makedirs(media_dir)
            logs.output_logs(f"Created directory: {media_dir}")
            
            # 创建 /mnt/zidoo/media/downloads 目录
            os.makedirs(downloads_dir)
            logs.output_logs(f"Created directory: {downloads_dir}")
            
            # 创建 /mnt/zidoo/media/downloads/movies 和 /mnt/zidoo/media/downloads/tv
            os.makedirs(os.path.join(downloads_dir, "movies"))
            logs.output_logs("Created directory: /mnt/zidoo/media/downloads/movies")
            
            os.makedirs(os.path.join(downloads_dir, "tv"))
            logs.output_logs("Created directory: /mnt/zidoo/media/downloads/tv")
            
            # 创建 /mnt/zidoo/media/movies 和 /mnt/zidoo/media/tv
            os.makedirs(movies_dir)
            logs.output_logs(f"Created directory: {movies_dir}")
            
            os.makedirs(tv_dir)
            logs.output_logs(f"Created directory: {tv_dir}")
        
        except Exception as e:
            logs.output_logs(f"Error creating directories: {e}")
    else:
        logs.output_logs(f"{media_dir} already exists.")
