#!/bin/bash

# папка откуда будут браться новые обои
source_dir="/home/rusto/develop/background/source/"

# и папка куда будут складываться обработанные
target_dir="/home/rusto/develop/background/target/"

# создаем список файлов для конвертации
SOURCE_FILES=( $(ls $source_dir*.jpg) )

i=1

# проходим циклом по файлам
for raw_file in ${SOURCE_FILES[@]}
do
    # подгоняем картинку под размер экрана
    convert -sample 800x480 $raw_file $target_dir$i.png

    # удаляем исходник
    rm $raw_file
    ((i++))
done
