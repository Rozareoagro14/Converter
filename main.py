import os
import subprocess
from moviepy.editor import VideoFileClip


# Функция для выбора оптимального битрейта видео
def choose_optimal_bitrate(input_video_path, target_file_size):
    # Получаем информацию о первом видео
    video_clip = VideoFileClip(input_video_path)
    video_duration = video_clip.duration
    video_size = os.path.getsize(input_video_path) / (1024 * 1024)  # Размер в МБ
    video_clip.close()

    # Вычисляем средний битрейт для целевого размера файла
    target_bitrate = (target_file_size * 1024 * 8) / video_duration  # В кбит/с

    return target_bitrate


# Создаем папку для конечных видеофайлов
output_dir = r'D:\Bots\Converter2'
os.makedirs(output_dir, exist_ok=True)

# Путь к папке с исходными видео
input_folder = r'D:\Bots\Converter2\pest'

# Получаем список видеофайлов в папке
video_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

# Полный путь к ffmpeg.exe
ffmpeg_path = r'D:\Bots\Converter2\ffmpeg-2024-02-04-git-7375a6ca7b-full_build\bin\ffmpeg.exe'

# Загружаем первое видео для выбора звуковой дорожки
first_video_file = os.path.join(input_folder, video_files[0])
first_video_clip = VideoFileClip(first_video_file)
first_audio_clip = first_video_clip.audio
print(f'Выберите звуковую дорожку для всех видео: {first_audio_clip.fps} fps')
selected_audio_track = int(input('Введите номер выбранной звуковой дорожки: '))
first_video_clip.close()

# Целевой размер файла в МБ (4 ГБ)
target_file_size_mb = 4096

# Проходим по всем видеофайлам
for video_file in video_files:
    # Получаем полный путь к исходному видео
    input_video = os.path.join(input_folder, video_file)

    # Загружаем видео с помощью moviepy
    video_clip = VideoFileClip(input_video)

    # Генерируем имя выходного файла на основе имени исходного файла
    output_video_name = os.path.splitext(video_file)[0] + '_selected_audio_H265_AAC.mp4'
    output_video = os.path.join(output_dir, output_video_name)

    # Выбираем оптимальный битрейт для видео
    optimal_bitrate = choose_optimal_bitrate(input_video, target_file_size_mb)

    # Команда для кодирования видео с оптимальными настройками
    ffmpeg_video_command = [
        ffmpeg_path,
        '-y',
        '-hwaccel', 'cuda',  # Использование CUDA для аппаратного ускорения
        '-i', input_video,
        '-vf', 'format=yuv420p',  # Преобразование в YUV420P
        '-c:v', 'hevc_nvenc',  # Использование кодека H.265 для кодирования GPU
        '-b:v', f'{optimal_bitrate}k',  # Целевой битрейт видео
        '-preset', 'slow',  # Установка медленной скорости кодировки для повышения качества
        '-c:a', 'aac',  # Кодирование аудио в AAC
        '-ac', '2',  # Сохранение аудио в формате стерео (2 аудиоканала)
        '-q:a', '1',  # Качество аудио
        '-max_muxing_queue_size', '1024',  # Установка максимального размера очереди мультиплексирования
        '-avoid_negative_ts', 'make_zero',  # Избегать отрицательных временных меток
        '-movflags', '+faststart',  # Установка флагов для быстрого начала воспроизведения
        '-map_metadata', '0',  # Копирование метаданных без изменений
        '-map_chapters', '0',  # Копирование глав без изменений
        '-f', 'mp4',  # Установка формата контейнера на MP4
        '-fs', f'{target_file_size_mb}M',  # Установка максимального размера файла
        '-strict', 'experimental',
        '-b:a', '512k',  # битрейт аудио
        '-map', '0:v:0', '-map', f'0:a:{selected_audio_track}',
        output_video
    ]

    # Запускаем процесс кодирования видео
    process = subprocess.Popen(ffmpeg_video_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)

    # Ждем завершения процесса и получаем вывод
    for stdout_line in process.stdout:
        print(stdout_line, end='')

    # Ждем завершения процесса
    process.communicate()

print('Все видео успешно конвертированы!')
