# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][1],
and this project adheres to [Semantic Versioning][2].

#### English
[show in Russian (отобразить на русском языке)][4]
## [Unreleased]
Section to track upcoming changes

##### User Interface:
- Add Russian localization since beginners are more comfortable with native language.
- Additional configuration window to set up: 
   - what type of "Russian to English" cards to create: with typing answer or without;
   - choose from-to dates for importing words;
   - option to highlight the word in context;
- Improve error messages by narrowing down the reason.

##### Import:
- Add user dictionaries (wordsets) as tags.
- Save problem words in json format and ask to retry downloading only them.
- Improve duplicate search to automatically update notes when any information was changed.

## [2.2.2] - 2020-03-05
### Changed
- Updated to a new API for authorization.

## [2.2.1] - 2019-12-03
### Changed
- Remove unnecessary error message when no words received.
- Fix dictionary loading for Anki 2.0.52.

## [2.2.0] - 2019-11-20
### Added
- Ability to choose what API to use.
- Check for new version on start.
- Show version info in the window title.
- Config option for number of words per request.
- Config options for download timeout, number of retries, sleep seconds and parallel downloads.
- Get word context again by using old API.
- Show busy progress bar when requesting list of words and wordsets.
- Show number of found words in a progress bar. 

### Changed
- Media is downloaded 3 times faster because of parallel downloads. 
- List of words and wordsets is requested asynchronously and doesn't freeze the GUI.
- "Update existing notes" option will update not only media, but also translation and context.
- Renamed 'All' radio-button to 'Any'.
- Improved dictionary word count in wordset window. 

## [2.1.5] - 2019-07-30
### Added
- Show combined translations (as in the web version).
- Moved to a new API.

### Removed
- Currently, word context is not downloaded. (Will be back in the future versions)

## [2.1.4] - 2019-07-12
### Changed
- Fixed import error for words without a transcription.
- Fixed import error for words with broken media links.
- Stop downloading a default picture for the translations without pictures.

## [2.1.3] - 2019-06-05
### Changed
- Fixed import error when there is no translation for the word (or phrase).

## [2.1.2] - 2019-05-29
### Changed
- Fixed media downloading for very long sentences (some audio were not downloaded because urls contain newline symbols).
- Show English answer for Russian to English cards (for new users of add-on only).

## [2.1.1] - 2019-05-19
### Changed
- Fixed connection issue on MacOS.

### Removed
- Protocol setting in config, since LinguaLeo doesn't work with http anymore.

## [2.1.0] - 2019-05-17
### Added
- Updated to a new API because of LinguaLeo update on 30.04.2019.
- Added option (radiobutton) for downloading "New" words.

### Changed
- Renamed "Studied" and "Unstudied" options to "Learned" and "Learning".
- List of user dictionaries shows number of learned words to download (if "Learned" option is selected).
- A list of words to download by status ("New", "Learning" or "Learned") is loading faster now. 
- For new users of add-on, Russian to English cards don't require typing a correct answer by default.

##[2.0.1] - 2019-05-04
### Changed
- Fixed connection issue on MacOS.
- Changed default protocol to https.

## [2.0.0] - 2019-04-10
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

#### Russian
[show in English][3]
## [Неизданное]
В этом разделе будут записываться изменения, которые ожидаются в будущих релизах. 

##### Пользовательский интерфейс:
- Русский язык интерфейса, так как начинающим комфортнее работать с дополнением на родном языке.
- Дополнительное окно конфигурации для установки настроек импорта, таких как: 
   - какого типа карточки создавать: с вводом ответа или без (для русско-английских карточек);
   - выбор промежутка времени для импортирования слов;
   - опция подсветки слова в контексте;
- Уточнить сообщения об ошибках.

##### Загрузка слов:
- Добавлять пользовательские словари как теги.
- Сохранять проблемные слова в json формате и предлагать пользователю попытаться снова скачать только проблемные слова.
- Исправить функцию поиска дупликатов, чтобы автоматически обновлять карточки при любых изменениях (не только медиа).

## [2.2.2] - 2020-03-05
### Изменено
- Обновлена авторизация в связи с изменением API.

## [2.2.1] - 2019-12-03
### Изменено
- Не отображать сообщение об ошибке, если отсутствуют слова выбранной категории.
- Исправлена загрузка списка словарей в старой версии Anki (2.0.52).

## [2.2.0] - 2019-11-20
### Добавлено
- Возможность выбрать API (новый или старый) для соединения с LinguaLeo.
- Проверка наличия новой версии при запуске дополнения.
- Отображение версии дополнения и напоминания перезапустить Anki для завершения установки обновления.
- Параметр в конфиге для количества слов за один запрос (при загрузке списка слов). На текущий момент сервис LinguaLeo работает нестабильно и изменения этого параметра поможет найти "потерянные" слова.
- Параметр в конфиге для таймаута запроса, количества попыток и длительности ожидания перед повторным скачиванием.
- Снова можно загружать контекст для слов (при использовании старого API).
- Сообщение "Загружается...", уведомляющее пользователя, что список слов или словарей загружается (актуально для больших списков либо медленного интернета).
- Отображение количества слов во время загрузки. 

### Изменено
- Картинки и звуки загружаются до 3-ёх раз быстрее благодаря многопоточности. 
- Список слов и словарей запрашивается асинхронно и не тормозит пользовательский интерфейс.
- "Update existing notes" опция обновляет не только картинки и звуки, но также перевод(ы), контекст и транскрипцию.
- Кнопка 'All' переименована на 'Any'.
- Улучшено отображение количества слов для словарей. 

## [2.1.5] - 2019-07-30
### Добавлено
- Импорт всех выбранных переводов для слова (так же как на сайте Lingualeo).
- Из-за обновлений на сервере пришлось снова переехать на новый API.

### Удалено
- На данный момент контекст слова не загружается. (Вернётся в следующих версиях)

## [2.1.4] - 2019-07-12
### Изменено
- Исправлена ошибка, возникающая при загрузке слов без транскрипции.
- Исправлена ошибка, возникающая из-за некорректных ссылок на медиа файлы.
- Исправлена загрузка изображения по-умолчанию для слов без изображения.

## [2.1.3] - 2019-06-05
### Изменено
- Исправлена ошибка при загрузке в случае, когда у слова (или предложения) нет перевода.

## [2.1.2] - 2019-05-29
### Изменено
- Исправлена загрузка медиафайлов для очень длинных предложений (так как URL-ссылка может содержать символы новой строки).
- Исправлен показ ответа на английском для карточек ru -> en (только для новых пользователей дополнения).

## [2.1.1] - 2019-05-19
### Изменено
- Исправлена ошибка соединения на MacOS, связанная с отсутствием сертификатов.

### Удалено
- Настройка протокола соединения в конфигурационном файле, так как LinguaLeo больше не работает с http.

## [2.1.0] - 2019-05-17
### Добавлено
- Аддон переехал на новый API в связи с обновлением LinguaLeo от 30.04.2019.
- Добавлена опция "New" для загрузки новых слов (как в сервисе LinguaLeo).

### Изменено
- Изменены названия опций "Studied" и "Unstudied" на "Learned" и "Learning" соответственно.
- При выборе опции "Learned" и нажатии "Import from Dictionaries" список словарей показывает кол-во изученных слов.
- Загрузка списка слов из категорий "New", "Learning" и "Learned" занимает меньше времени (особенно для больших словарей).
- Для новых пользователей дополнения, создаваемые карточки не требуют печатать правильный ответ на английском. 

## [2.0.1] - 2019-05-04
### Изменено
- Исправлена ошибка соединения на MacOS.
- Https протокол используется по-умолчанию.

## [2.0.0] - 2019-04-10
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