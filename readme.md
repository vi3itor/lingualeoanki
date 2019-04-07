# Import Words From LinguaLeo to Anki 2.0

#####English / [Russian](#russian)

### Description ###

This is an add-on for [Anki](https://apps.ankiweb.net/) - powerful, intelligent flash cards, that makes remembering things easy.

The add-on downloads your dictionary words from [LinguaLeo](https://lingualeo.com/) - another great resource to learn English and transforms them into Anki cards. Cards are created both for 'english to russian' and 'russian to english' sides and include pronunciation, images, transcription and context.

### Installation ###

To install this add-on, open Anki on your computer, go to the Tools menu and then Add-ons > Open Add-ons Folder and put the source code there. 

Watch this gif for the details (with russian captures):

[how to install the plugin](https://media.giphy.com/media/3oFzm4JamA2wb86yTS/giphy.gif)

But the easiest way to install the plugin is by using the Anki's built-in add-ons system. Check it out on the plugin page on [Anki add-ons forum](https://ankiweb.net/shared/info/1411073333).

### Usage ###

To download your words simply go to the Tools menu > Import from LinguaLeo, enter your login and password for the site and that's all. You don't need to create decks, models, templates or anything else. The add-on will make it all for you. As simple as that. 

You can also choose whether you want to download all words from your LinguaLeo dictionary or only unstudied ones.

Please, be patient, it can take up to 10 minutes to download 1000 words due to size of images and sounds. 

### Compatibility ###

This add-on only works with Anki's stable release branch (2.0.x ≥ 2.0.44). The 2.1 beta branch is not supported at this point in time.

### Meta ###

Feel free to write me about add-on or anything else here on [bitbucket](https://bitbucket.org/alex-altay/) or [vk](https://vk.com/trutanov.alex).

This project is licensed under the GPL License - see the [LICENSE](https://bitbucket.org/alex-altay/lingualeoanki/src/70f0add7da031166f3fbd50dfd8e634236488840/LICENSE?at=master&fileviewer=file-view-default) file for details. 

### Acknowledgments ###

[Ilya Isaev](https://github.com/relaxart) for [inspiration](https://habrahabr.ru/post/276495/) and his project [LeoPort](https://github.com/relaxart/LeoPort).
[Nikolay Bikov](https://github.com/bikenik) and everyone who helps with testing on MacOs.

#####Russian / [English](#english)
### Описание

Дополнение для [Anki](https://apps.ankiweb.net/) - программы для облегчения запоминания слов, выражений и любой другой информации с помощью интервальных повторений.

Дополнение позволяет в один клик скачать ваши сохранённые слова из [LinguaLeo](https://lingualeo.com/), другой замечательной образовательной платформы для изучения и практики английского, и создать для них карточки Anki. Карточки создаются как в варианте "русский - английский", так и "английский - русский" и включают в себя изображения, транскрипцию, аудио с произношением и предложение с контекстом из ЛингваЛео.   

ЛингваЛео имеет удобный интерфейс для добавления новых слов и неплохое расширение для браузера для перевода незнакомых слов и мгновенного добавления в словарь вместе с контекстом. Но после того, как вы добавили слова и изучили их с помощью нескольких типов тренировок, Анки поможет вам никогда не забыть эти слова с минимальной затратой времени и усилий.

###Новое в версии 2.0:
#### Добавлено
- Полная поддержка Anki 2.1.x и Anki 2.0 (тестировалось на Anki 2.0.52).
- Возможность импортировать не только все слова, но выбирать пользовательские словари (наборы) для импорта.
- Кнопки "Войти" и "Выйти", а также опция оставаться в системе (сохраняя cookies в папке user\_files).
- Возможность выбрать, какие слова импортировать: 'Изученные', 'Неизученные' или 'Любые'.
- Опция "Обновить существующие карточки", чтобы обновить медиафайлы.
- Конфигурационный файл для хранения логина, пароля (если выбрана соответствующая опция), а также других пользовательских настроек (оставаться в системе, протокол (http либо https), и другие) 
- Библиотека Six.py для удобного написания совместимого кода для Python 2 и 3.
- Changelog для ведения лога изменений программы.

#### Изменено
- Исправлена загрузка дупликатов.
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

Если вы по какой-то причине хотите установить дополнение вручную: скачайте архив с исходным кодом из репозитория на [github](https://github.com/vi3itor/lingualeoanki/) либо на [bitbucket](https://bitbucket.org/vkhaustov/lingualeoanki/), откройте Anki на вашем компьютере, выберите пункт меню:   
в Anki 2.1.x "Инструменты" (Tools) > "Дополнения" (Add-ons) и кликните на кнопку "Просмотреть файлы" (View Files)  
в Anki 2.0 "Инструменты" (Tools) > "Дополнения" (Add-ons) > "Открыть папку с дополнениями" (Open Add-ons Folder)  
и скопируйте туда содержимое архива. Для Anki 2.1.x убедитесь, что вы копируете в папку "addons21". Перезапустите программу.

Гифка с наглядным изображением процесса ручной установки для Anki 2.0:  
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

Для того, чтобы оценить дополнение и оставить комментарий перейдите на [его страницу](https://ankiweb.net/shared/info/1411073333), войдите в аккаунт AnkiWeb в правом верхнем углу и кликните Rate this. Но если вы хотите новую функцию или обнаружили ошибку, пожалуйста, не оставляйте сообщение о ней в комментариях, а скопируйте текст ошибки и создайте issue на [github](https://github.com/vi3itor/lingualeoanki/issues/new), либо напишите мне на email: 4yourquestions [собачка] gmail.com. 

Свободное копирование и использование. Лицензия [GPL](https://github.com/vi3itor/lingualeoanki/blob/master/LICENSE). 

### Авторы
Версия 1: [Александр Трутанов](https://vk.com/trutanov.alex), оригинальный проект на [bitbucket](https://bitbucket.org/alex-altay/lingualeoanki).    
Версия 2: [Виктор Хаустов](https://github.com/vi3itor/), проект на [GitHub](https://github.com/vi3itor/lingualeoanki/).

### Благодарности ###

[Илья Исаев](https://github.com/relaxart) за [вдохновение](https://habrahabr.ru/post/276495/) и проект [LeoPort](https://github.com/relaxart/LeoPort).  
[Serge](https://bitbucket.org/pioneer/) за функцию поиска дупликатов, поддержку слов с апострофом и функцию повторного скачивания слов.   
[Николай Байков](https://github.com/bikenik) за [PostMan Collection](https://github.com/bikenik/alfred-lingualeo/blob/master/Lingua-Leo.postman_collection.json), дополнение [alfred-lingualeo](https://github.com/bikenik/alfred-lingualeo) и за помощь с тестированием на MacOs.   
А также всем, кто пользовался приложением, оставлял ценные комментарии и помогал тестировать на различных платформах.