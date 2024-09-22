import os
import importlib.util
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_python_files(directory):

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
            logging.warning(f'Переменная CMDS не найдена: {file_path}')
            return []
    except Exception as e:
        logging.error(f'Ошибка при получении команд из файла {file_path}: {e}')
        return []

def execute_commands(cmds):
    executed_commands = set()
    
    for cmd in cmds:
        if cmd in executed_commands:
            logging.info(f'Команда "{cmd}" уже была выполнена, далее.')
            continue
        
        logging.info(f'Выполнение команды: {cmd}')
        try:
            executed_commands.add(cmd)  # Добавляем команду перед выполнением
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f'Ошибка при выполнении команды "{cmd}": {e}')

def main(directory):
    all_cmds = []
    
    python_files = find_python_files(directory)   # Поиск всех Python-файлов

    for file in sorted(python_files):              # Извлечение команд из файлов
        cmds = extract_cmds_from_file(file)
        all_cmds.extend(cmds)
    
    unique_sorted_cmds = sorted(set(all_cmds))          # Удаление дублей
    
    execute_commands(unique_sorted_cmds)                    # Выполнение команд

if __name__ == "__main__":
    directory_path = input("Указать путь к директории с Python-файлами: ")
    
    if os.path.isdir(directory_path):
        main(directory_path)
    else:
        logging.error("Указанный путь не является директорией.")
