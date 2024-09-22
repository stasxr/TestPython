import os
import importlib.util
import subprocess
import logging
import time  # Для добавления задержки между попытками

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_python_files(directory):
    """Ищет все Python-файлы в указанной директории."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    logging.info(f'Найдено {len(python_files)} Python-файлов.')
    return python_files

def extract_cmds_from_file(file_path):
    spec = importlib.util.spec_from_file_location("module.name", file_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        cmds = getattr(module, 'CMDS', None)
        if isinstance(cmds, list):
            logging.info(f'Извлечены команды из файла: {file_path}')
            return cmds
        else:
            logging.warning(f'Переменная CMDS не найдена или не является списком в файле: {file_path}')
            return []
    except Exception as e:
        logging.error(f'Ошибка при извлечении команд из файла {file_path}: {e}')
        return []

def execute_command_with_retry(cmd, retries=3, delay=1):
    for attempt in range(retries):
        try:
            subprocess.run(cmd, shell=True, check=True)
            break  
        except subprocess.CalledProcessError as e:
            logging.error(f'Ошибка при выполнении команды "{cmd}": {e}')
            if attempt < retries - 1:
                logging.info(f'Повторная попытка {attempt + 1} для команды "{cmd}" через {delay} секунд...')
                time.sleep(delay) 
            else:
                logging.error(f'Команда "{cmd}" не выполнена после {retries} попыток')

def execute_commands(cmds, retries=3, delay=1):

    executed_commands = set()
    
    for cmd in cmds:
        if cmd not in executed_commands:
            logging.info(f'Выполнение команды: {cmd}')
            execute_command_with_retry(cmd, retries, delay)
            executed_commands.add(cmd)
        else:
            logging.info(f'Команда "{cmd}" уже была выполнена, пропускаем.')

def main(directory, retries=3, delay=1):
    all_cmds = []
    
    python_files = find_python_files(directory)            # Поиск всех Python-файлов

    for file in sorted(python_files):                      # Извлечение команд из файлов
        cmds = extract_cmds_from_file(file)
        all_cmds.extend(cmds)
    
    unique_sorted_cmds = sorted(set(all_cmds))                 # Удаление дубликатов
    
    execute_commands(unique_sorted_cmds, retries, delay)             # Выполнение команд с указанным количеством повторных попыток и задержкой

if __name__ == "__main__":
    directory_path = input("Введите путь к директории с Python-файлами: ")
    
    if os.path.isdir(directory_path):                   # количество попыток выполнения (по умолчанию 10)
        retries = int(input("Введите количество повторных попыток для каждой команды (по умолчанию 10): ") or 10)
        delay = int(input("Введите интервал времени между попытками (в секундах, по умолчанию 3): ") or 3)                    # задержка между попытками (по умолчанию 3 секунды)
        main(directory_path, retries, delay)
    else:
        logging.error("Указанный путь не является директорией.")
