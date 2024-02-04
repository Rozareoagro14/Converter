import os
import subprocess

# Создание папки FILM
output_dir = 'E:\_FILM\The_Boys_S01_2019'
os.makedirs(output_dir, exist_ok=True)

# Путь к исходной папке с видео
input_folder = r"F:\_film_ORIG\The_Boys_S01_2019_BDRip-AVC_KvK_by_Dalemake"

# Получение списка файлов в папке
video_files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

for video_file in video_files:
    # Путь к исходному видео
    input_video = os.path.join(input_folder, video_file)

    # Генерация имени выходного видео на основе имени исходного файла
    output_video = os.path.join(output_dir, os.path.splitext(video_file)[0] + '.mp4')

    # Команда для извлечения видео  с оптимальными настройками
    ffmpeg_video_command = [
        'ffmpeg',
        '-y',
        '-hwaccel', 'cuda',  # Использование CUDA для аппаратного ускорения
        '-c:v', 'h264_cuvid',  # Использование кодека NVDEC для декодирования
        '-i', input_video,
        '-vf', 'format=yuv420p',  # Преобразовать в 8-битное видео
        '-c:v', 'h264_nvenc',  # Использование кодека NVENC для кодирования
        '-preset', 'slow',  # Установка медленной скорости кодировки для повышения качества
        '-b:v', '4M',  # Целевой битрейт видео (можно настроить в зависимости от требуемого качества)
        '-maxrate', '8M',  # Максимальный битрейт видео (позволяет динамически увеличивать битрейт при необходимости)
        '-bufsize', '12M',  # Размер буфера для контроля битрейта (можно настроить в зависимости от требуемого качества)
        '-c:a', 'libmp3lame',  # Использование кодека MP3 для аудио
        '-q:a', '1',  # Качество аудио (1-9, где 1 - наилучшее качество, 9 - наихудшее)
        '-max_muxing_queue_size', '1024',  # Установка максимального размера очереди мультиплексирования
        '-avoid_negative_ts', 'make_zero',  # Избегать отрицательных временных меток
        '-movflags', '+faststart',  # Установка флагов для быстрого начала воспроизведения
        '-map_metadata', '0',  # Копирование метаданных без изменений
        '-map_chapters', '0',  # Копирование глав без изменений
        '-f', 'mp4',  # Установка формата контейнера на MP4
        '-fs', '8G',  # Установка максимального размера файла на 4 GB
        output_video
    ]

    process = subprocess.Popen(ffmpeg_video_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True, encoding='utf-8')  # Указываем кодировку utf-8

    print('Извлечение видео началось:')
    for line in process.stdout:
        # Вывод информации о текущем состоянии процесса кодирования
        print(line.strip())
    process.wait()
    print('Извлечение видео завершено.')

    # Открытие папки с полученным аудиофайлом
subprocess.Popen(['explorer', output_dir])
