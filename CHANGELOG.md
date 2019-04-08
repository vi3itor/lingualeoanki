# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][1],
and this project adheres to [Semantic Versioning][2].

[English][3] / [Russian][4]
## English
## [Unreleased]
Section to track upcoming changes 

## [2.0.0] - 2019-04-xx
### Added
- Full support of Anki 2.1.x and Anki 2.0 (tested on Anki 2.0.52).
- Ability to import not only all words, but words from one or several user dictionaries (word sets).
- Log in and log out buttons and ability to stay logged in (by storing cookies in the user\_files folder).
- Select words to import: "Studied", "Unstudied" or "Any".
- Option to update existing notes (see also "Changed" section).
- Configuration file to store user's login and (optionally) password as well as other settings: stay logged in, protocol (http or https), remember the password.
- Six.py module for writing Python 2 and 3 compatible code easier.
- Changelog to keep updates and changes in one place.

### Changed
- Fixed issues with downloading duplicates.
- Check for duplicates first before starting to import words (don't check for duplicates only if "Update existing notes" option is selected).
- Prevent multiple runs of the add-on at the same time.
- When exiting allow Anki's main window to close add-on window if no words are downloading.

### Removed
- Option "missed words": by default the add-on only downloads media for the words that are not in the deck.

## [1.3.1] - 2019-01-04
### Changed
- Fixed crash on first run caused by "missed" words option.

## [1.3.0] - 2018-11-11
### Added
- Option to download "missed" words: continue downloading from last downloaded word.

## [1.2.0] - 2018-01-25
### Added
- Support for words with apostrophes.

### Changed
- Update pictures and sound for duplicate words only if they are different.

## [1.1.0] - 2018-01-06
### Added
- Check for duplicates while adding new words.
- Retry downloading pictures and sound for notes if initially failed. 

## [1.0.0] - 2017-12-28
### Added
- Download words from user's dictionary in LinguaLeo.
- Option to download unstudied words only.

## Russian
## [Неизданное]
В этом разделе будут записываться изменения, которые ожидаются в будущих релизах. 

## [2.0.0] - 2019-04-xx
### Добавлено
- Полная поддержка Anki 2.1.x и Anki 2.0 (тестировалось на Anki 2.0.52).
- Возможность импортировать не только все слова, но выбирать пользовательские словари (наборы) для импорта.
- Кнопки "Войти" и "Выйти", а также опция оставаться в системе (сохраняя cookies в папке user\_files).
- Возможность выбрать, какие слова импортировать: 'Изученные', 'Неизученные' или 'Любые'.
- Опция "Обновить существующие карточки", чтобы обновить медиафайлы.
- Конфигурационный файл для хранения логина, пароля (если выбрана соответствующая опция), а также других пользовательских настроек: оставаться в системе, протокол (http либо https). 
- Библиотека Six.py для удобного написания совместимого кода для Python 2 и 3.
- Changelog для ведения лога изменений программы.

### Изменено
- Исправлена загрузка дубликатов.
- Прежде чем загружать медиафайлы, дополнение проверяет, были ли эти слова загружены ранее (и не загружает медиафайлы для существующих слов, если опция "Обновить существующие карточки" неактивна).
- Невозможно запустить более одной копии дополнения одновременно.
- При выходе из Anki и отсутствии активных загрузок окно дополнения будет закрыто автоматически.

### Удалено
- Опция "missed words", так как по умолчанию дополнение создаёт карточки и загружает медиафайлы только для слов, которые не были импортированы ранее.

## [1.3.1] - 2019-01-04
### Изменено
- Исправлена ошибка при первом запуске дополнения, вызванная опцией "missed words".

## [1.3.0] - 2018-11-11
### Добавлено
- Опция "missed words" для загрузки с последнего удачно загруженного слова.

## [1.2.0] - 2018-01-25
### Добавлено
- Поддержка для слов с апострофом.

### Изменено
- Обновление медиафайлов (картинок либо звуков) в словах только в том случае, если они были обновлены пользователем.

## [1.1.0] - 2018-01-06
### Добавлено
- Проверка дубликатов при добавлении новых слов в коллекцию.
- При возникновении ошибки загрузки пытаться загрузить слова снова. 

## [1.0.0] - 2017-12-28
### Добавлено
- Загрузка слов из пользовательского словаря LinguaLeo.
- Опция загружать только неизученные слова.

[1]:	https://keepachangelog.com/en/1.0.0/
[2]:	https://semver.org/spec/v2.0.0.html
[3]:	#english
[4]:	#russian