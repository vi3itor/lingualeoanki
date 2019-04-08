# Import Words From LinguaLeo to Anki 2

### Description

[go to description in Russian](#russian)

This is an add-on for [Anki](https://apps.ankiweb.net/) - powerful, intelligent flash cards, that makes remembering things easy via space repetition.

The add-on downloads your dictionary words from [LinguaLeo](https://lingualeo.com/) - another great resource to learn English and transforms them into Anki cards. Cards are created both for 'english to russian' and 'russian to english' sides and include pronunciation, images, transcription and context.

[LinguaLeo](https://lingualeo.com/) has a user-friendly interface for adding new words to learn and a good browser [extensions](https://lingualeo.com/ru/browserapps) to quickly look up for translations and easily add words to the dictionary. But once you add the words and learned them via several [trainings](https://lingualeo.com/ru/training), you need Anki to stick them in your memory forever with as little time and effort as possible. 

### New in version 2.0:
#### Added
- Full support of Anki 2.1.x and Anki 2.0 (tested on Anki 2.0.52).
- Ability to import not only all words, but words from one or several user dictionaries (word sets).
- Log in and log out buttons and ability to stay logged in (by storing cookies in the user\_files folder).
- Select words to import: "Studied", "Unstudied" or "Any".
- Option to update existing notes (see also "Changed" section).
- Configuration file to store user's login and (optionally) password as well as other settings: stay logged in, protocol (http or https), remember the password.
- Six.py module for write Python 2 and 3 compatible code easier.
- Changelog to keep updates and changes in one place.

#### Changed
- Fixed issues with downloading duplicates.
- Check for duplicates first before starting to import words (don't check for duplicates only if "Update existing notes" option is selected).
- Prevent multiple runs of the add-on at the same time.
- When exiting allow Anki's main window to close add-on window if no words are downloading.

#### Removed
- Option "missed words": by default the add-on only downloads media for the words that are not in the deck.

The full log of changes can be found in the repository: [Changelog](https://github.com/vi3itor/lingualeoanki/blob/master/CHANGELOG.md)

### Installation

The easiest (and preferable) way to install the add-on is by using the Anki's built-in add-ons managing system. In this case you will automatically receive up-to-date version of add-on with the latest features and bug fixes. To install add-on go to:  
on Anki 2.1.x "Tools" > "Add-ons" > "Get add-ons..."   
on Anki 2.0 "Tools" > "Add-ons" > "Browse & Install"   
and input add-on's code: 1411073333. Restart Anki.

If for some reason you wish to install the add-on manually, download the archive with the latest version from the repository on [github](https://github.com/vi3itor/lingualeoanki/), open Anki on your computer, go to:   
on Anki 2.1.x "Tools" > "Add-ons" > "View Files"   
on Anki 2.0 "Tools" > "Add-ons" > "Open Add-ons Folder"   
and put the content of the archive there. For Anki 2.1.x make sure that you are copying it into "addons21" folder. Restart Anki.

Watch the following gif for the details of manual installation on Anki 2.0 (with russian captures):
[how to manually install](https://media.giphy.com/media/3oFzm4JamA2wb86yTS/giphy.gif)

### Compatibility

The add-on works with Anki 2.1.x and Anki 2.0 (tested on 2.0.52). It is recommended to install the latest version of Anki 2.1, because the future releases of the add-on may not support outdated Anki 2.0.52.

### Usage

To run the add-on go to the "Tools" menu and click "Import from LinguaLeo". Enter your login and password. If you'd like to stay logged in choose "Stay logged in" option, and you can also save the password (stored in the configuration file), and click "Log in" button.   
If the authorisation is successful, you can choose the words to import: "Studied", "Unstudied" or "Any".  
If you updated media for some notes that had been previously imported, choose "Update existing notes" option.  

To download all user words click "Import all words" button. If you want to choose user dictionaries (word sets) to download words from: click "Import from dictionaries" button and hold Ctrl (or Cmd) to choose several dictionaries. Then click "Import".   
And that's all. You don't need to create decks, models, templates or anything else. The add-on will make it all for you. As simple as that. 

Please, be patient, it can take up to 10 minutes (or even more) to download 1000 words depending on the size of images and sounds and the speed of your internet connection.  
When finished press "Exit" button.


### Additional

To rate this add-on and leave a feedback go to [its page](https://ankiweb.net/shared/info/1411073333), log in to your AnkiWeb account in top right corner and press "Rate this". If you'd like to see a new feature or found a bug, please, don't leave a comment on the add-on's page, rather copy an error message and create an issue on [github](https://github.com/vi3itor/lingualeoanki/issues/new), or send me an email to 4yourquestions [at] gmail.com. 

This project is licensed under the GPL License - see the [LICENSE](https://github.com/vi3itor/lingualeoanki/blob/master/LICENSE) file for details. 


### Authors 

Version 1: [Alex Trutanov](https://vk.com/trutanov.alex), original project on [bitbucket](https://bitbucket.org/alex-altay/lingualeoanki).    
Version 2: [Victor Khaustov](https://github.com/vi3itor/), project on [GitHub](https://github.com/vi3itor/lingualeoanki/).

### Acknowledgments

[Ilya Isaev](https://github.com/relaxart) for [inspiration](https://habrahabr.ru/post/276495/) and his project [LeoPort](https://github.com/relaxart/LeoPort). 
[Serge](https://bitbucket.org/pioneer/) for duplicate search feature, support words with apostrophes and function to redownload words if initially failed.   
[Nikolay Bikov](https://github.com/bikenik) for [PostMan Collection](https://github.com/bikenik/alfred-lingualeo/blob/master/Lingua-Leo.postman_collection.json), [alfred-lingualeo](https://github.com/bikenik/alfred-lingualeo) add-on and for helping to test on MacOS.   
And for all users who left valuable comments and feedback and helped to test on different platforms.

##### Russian 
[description in English](#description)

### Описание

Дополнение для [Anki](https://apps.ankiweb.net/) - программы для облегчения запоминания слов, выражений и любой другой информации с помощью интервальных повторений.

Дополнение позволяет в один клик скачать ваши сохранённые слова из [LinguaLeo](https://lingualeo.com/), другой замечательной образовательной платформы для изучения и практики английского, и создать для них карточки Anki. Карточки создаются как в варианте "русский - английский", так и "английский - русский" и включают в себя изображения, транскрипцию, аудио с произношением и предложение с контекстом из ЛингваЛео.   

[ЛингваЛео](https://lingualeo.com/) имеет удобный интерфейс для добавления новых слов и неплохое [расширение для браузера](https://lingualeo.com/ru/browserapps) для перевода незнакомых слов и мгновенного добавления в словарь вместе с контекстом. Но после того, как вы добавили слова и изучили их с помощью нескольких [тренировок](https://lingualeo.com/ru/training), Анки поможет вам никогда не забыть эти слова с минимальной затратой времени и усилий.

### Новое в версии 2.0:

#### Добавлено
- Полная поддержка Anki 2.1.x и Anki 2.0 (тестировалось на Anki 2.0.52).
- Возможность импортировать не только все слова, но выбирать пользовательские словари (наборы) для импорта.
- Кнопки "Войти" и "Выйти", а также опция оставаться в системе (сохраняя cookies в папке user\_files).
- Возможность выбрать, какие слова импортировать: 'Изученные', 'Неизученные' или 'Любые'.
- Опция "Обновить существующие карточки", чтобы обновить медиафайлы.
- Конфигурационный файл для хранения логина, пароля (если выбрана соответствующая опция), а также других пользовательских настроек: оставаться в системе, протокол (http либо https). 
- Библиотека Six.py для удобного написания совместимого кода для Python 2 и 3.
- Changelog для ведения лога изменений программы.

#### Изменено
- Исправлена загрузка дубликатов.
- Прежде чем загружать медиафайлы, дополнение проверяет, были ли эти слова загружены ранее (и не загружает медиафайлы для существующих слов, если опция "Обновить существующие карточки" неактивна).
- Невозможно запустить более одной копии дополнения одновременно.
- При выходе из Anki и отсутствии активных загрузок окно дополнения будет закрыто автоматически.

#### Удалено
- Опция "missed words", так как по умолчанию дополнение создаёт карточки и загружает медиафайлы только для слов, которые не были импортированы ранее.

Полный лог изменений можно найти в репозитории: [Changelog](https://github.com/vi3itor/lingualeoanki/blob/master/CHANGELOG.md#russian)

### Установка

Наиболее простой (и предпочтительный) способ установки: с помощью системы управления дополнениями Anki. В таком случае вы сможете автоматически получать обновления с исправлением ошибок и новыми функциями. Для этого выберите пункт меню программы:  
в Anki 2.1.x "Инструменты" (Tools) > "Дополнения" (Add-ons) > "Скачать дополнения" (Get Add-ons...)  
в Anki 2.0 "Инструменты" (Tools) > "Дополнения" (Add-ons) > "Обзор и установка" (Browse & Install)  
введите код 1411073333 и перезапустите Anki.  

Если вы по какой-то причине хотите установить дополнение вручную: скачайте архив с исходным кодом из репозитория на [github](https://github.com/vi3itor/lingualeoanki/), откройте Anki на вашем компьютере, выберите пункт меню:   
в Anki 2.1.x "Инструменты" (Tools) > "Дополнения" (Add-ons) и кликните на кнопку "Просмотреть файлы" (View Files)  
в Anki 2.0 "Инструменты" (Tools) > "Дополнения" (Add-ons) > "Открыть папку с дополнениями" (Open Add-ons Folder)  
и скопируйте туда содержимое архива. Для Anki 2.1.x убедитесь, что вы копируете в папку "addons21". Перезапустите программу.

Гифка с наглядным изображением процесса ручной установки для Anki 2.0
[Как установить дополнение вручную](https://media.giphy.com/media/3oFzm4JamA2wb86yTS/giphy.gif)

### Совместимость

Дополнение работает с новыми версиями (Anki 2.1.x), а также с Анки 2.0 (тестировалось на 2.0.52).
Рекомендуется установить Anki 2.1, актуальную версию программы, так как новые версии дополнения могут не поддерживать устаревшую версию Anki 2.0. 

### Как это работает? 

После установки, чтобы импортировать ваши слова из LinguaLeo в Anki, откройте меню "Инструменты" (Tools) и выберите пункт "Import from LinguaLeo". Введите ваш логин и пароль для сервиса LinguaLeo. Если вы хотите оставаться в системе, выберите пункт "Stay logged in", и если вы хотите, чтобы дополнение запомнило пароль, выберите "Save password" (в таком случае пароль будет храниться в конфигурационном файле), после этого нажмите "Log in".   
Если авторизация прошла успешно, вы можете выбрать какие слова импортировать: "Studied" (изученные), "Unstudied" (неизученные) либо "Any" (и те и другие). 
Если в некоторых словах вы обновили изображение или звук и хотите, чтобы эти изменения попали в Anki, выберите пункт "Update existing notes".   

Для того, чтобы импортировать все слова, нажмите кнопку "Import all words". Для того, чтобы выбрать словари (наборы) для импорта, нажмите "Import from dictionaries" и выберите один или несколько наборов (удерживая клавишу Ctrl либо Cmd) и нажмите "Import".
Никаких моделей, шаблонов, колод создавать не нужно, дополнение сделает всю работу за вас. Проще некуда.

Наберитесь терпения. Импорт 1000 слов может занять 10 минут и более в зависимости от веса аудио с произношением и картинок и скорости вашего интернета.  
По окончании работы с дополнением нажмите "Exit".

### Кроме того

Для того, чтобы оценить дополнение и оставить комментарий перейдите на [его страницу](https://ankiweb.net/shared/info/1411073333), войдите в аккаунт AnkiWeb в правом верхнем углу и кликните Rate this. Но если вы хотите новую функцию или обнаружили ошибку, пожалуйста, не оставляйте сообщение о ней в комментариях, а скопируйте текст ошибки и создайте issue на [github](https://github.com/vi3itor/lingualeoanki/issues/new), либо напишите на email: 4yourquestions [собачка] gmail.com. 

Свободное копирование и использование. Лицензия [GPL](https://github.com/vi3itor/lingualeoanki/blob/master/LICENSE). 

### Авторы

Версия 1: [Александр Трутанов](https://vk.com/trutanov.alex), оригинальный проект на [bitbucket](https://bitbucket.org/alex-altay/lingualeoanki).    
Версия 2: [Виктор Хаустов](https://github.com/vi3itor/), проект на [GitHub](https://github.com/vi3itor/lingualeoanki/).

### Благодарности

[Илья Исаев](https://github.com/relaxart) за [вдохновение](https://habrahabr.ru/post/276495/) и проект [LeoPort](https://github.com/relaxart/LeoPort).  
[Serge](https://bitbucket.org/pioneer/) за функцию поиска дубликатов, поддержку слов с апострофом и функцию повторного скачивания слов.   
[Николай Байков](https://github.com/bikenik) за [PostMan Collection](https://github.com/bikenik/alfred-lingualeo/blob/master/Lingua-Leo.postman_collection.json), дополнение [alfred-lingualeo](https://github.com/bikenik/alfred-lingualeo) и за помощь с тестированием на MacOs.   
А также всем, кто пользовался приложением, оставлял ценные комментарии и помогал тестировать на различных платформах.