import os
import subprocess
from moviepy.editor import VideoFileClip

# Создание папки FILM
output_dir = r'D:\Bots\Converter2'
os.makedirs(output_dir, exist_ok=True)

# Путь к исходной папке с видео
input_folder = r'D:\Bots\Converter2\pest'

# Получение списка файлов в папке
video_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

# Полный путь к ffmpeg.exe
ffmpeg_path = r'D:\Bots\Converter2\ffmpeg-2024-02-04-git-7375a6ca7b-full_build\bin\ffmpeg.exe'

# Загрузка первого видео для выбора аудиодорожки
first_video_file = os.path.join(input_folder, video_files[0])
first_video_clip = VideoFileClip(first_video_file)
first_audio_clip = first_video_clip.audio
print(f'Выберите звуковую дорожку для всех видео: {first_audio_clip.fps} fps')
selected_audio_track = int(input('Введите номер выбранной звуковой дорожки: '))
first_video_clip.close()

for video_file in video_files:
    # Путь к исходному видео
    input_video = os.path.join(input_folder, video_file)

    # Загрузка видео с использованием moviepy
    video_clip = VideoFileClip(input_video)

    # Генерация имени выходного видео на основе имени исходного файла
    output_video = os.path.join(output_dir, os.path.splitext(video_file)[0] + '_selected_audio.mp4')

    # Команда для извлечения видео с оптимальными настройками
    ffmpeg_video_command = [
        ffmpeg_path,
        '-y',
        '-hwaccel', 'cuda',  # Использование CUDA для аппаратного ускорения
        # '-c:v', 'h264_cuvid',  # Использование кодека NVDEC для декодирования
        '-i', input_video,
        '-vf', 'format=yuv420p',  # Преобразование в YUV420P
        # '-c:v', 'h264_nvenc',  # Использование кодека NVENC для кодирования
        # '-c:v', 'libx265', # Использование кодека H.265 для кодирования CPU
        '-c:v', 'hevc_nvenc', # Использование кодека H.265 для кодирования GPU
        '-preset', 'slow',  # Установка медленной скорости кодировки для повышения качества
        # '-b:v', '4M',  # Целевой битрейт видео (можно настроить в зависимости от требуемого качества)
        '-b:v', '8M',  # Целевой битрейт видео (можно настроить в зависимости от требуемого качества)
        # '-maxrate', '8M',  # Максимальный битрейт видео (позволяет динамически увеличивать битрейт при необходимости)
        '-maxrate', '10M',  # Максимальный битрейт видео (позволяет динамически увеличивать битрейт при необходимости)
        '-bufsize', '12M',
        # Размер буфера для контроля битрейта (можно настроить в зависимости от требуемого качества)
        # '-c:a', 'libmp3lame',  # Кодирование аудио в MP3
        '-c:a', 'aac',  # Кодирование аудио в AAC
        '-ac', '2',  # Сохранение аудио в формате стерео (2 аудиоканала)
        '-q:a', '1',  # Качество аудио (1-9, где 1 - наилучшее качество, 9 - наихудшее)
        '-max_muxing_queue_size', '1024',  # Установка максимального размера очереди мультиплексирования
        '-avoid_negative_ts', 'make_zero',  # Избегать отрицательных временных меток
        '-movflags', '+faststart',  # Установка флагов для быстрого начала воспроизведения
        '-map_metadata', '0',  # Копирование метаданных без изменений
        '-map_chapters', '0',  # Копирование глав без изменений
        '-f', 'mp4',  # Установка формата контейнера на MP4
        '-fs', '4G',  # Установка максимального размера файла на 4 GB
        '-strict', 'experimental',
        # '-b:a', '192k',
        # '-b:a', '320k',
        '-b:a', '512k',  # битрейт аудио
        '-map', '0:v:0', '-map', f'0:a:{selected_audio_track}',
        output_video
    ]

    process = subprocess.Popen(ffmpeg_video_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True, encoding='utf-8')  # Указываем кодировку utf-8

    print(f'Извлечение видео из {video_file} началось:')
    for line in process.stdout:
        # Вывод информации о текущем состоянии процесса кодирования
        print(line.strip())
    process.wait()
    print(f'Извлечение видео из {video_file} завершено с выбранной звуковой дорожкой.')

# Открытие папки с полученными видеофайлами
subprocess.Popen(['explorer', output_dir])
