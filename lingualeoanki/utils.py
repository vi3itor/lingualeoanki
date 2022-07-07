import os
import json
from .six.moves import urllib
import socket
import ssl
import time

from aqt import mw
from aqt.utils import showInfo  # TODO: remove when search problem is fixed
from anki import notes

try:
    from anki.rsbackend import InvalidInput  # TODO: Check if it actually breaks earlier versions
except ImportError:
    # define our class to avoid error on earlier versions
    class InvalidInput(Exception):
        pass

from . import styles
from ._version import VERSION


fields = ['en', 'transcription',
          'ru', 'picture_name',
          'sound_name', 'context']

# TODO: Check anki versioning and find a better fix
try:
    from anki import buildinfo
    anki_version = buildinfo.version.split('.')[-1]
    anki_version = int(anki_version)
except:
    print("Can't find or parse anki_version")
    # it means that it's definitely less than 2.1.23
    anki_version = 20


def create_templates(collection):
    # TODO: Generate template names based on a language pair
    template_eng = collection.models.new_template('en -> ru')
    template_eng['qfmt'] = styles.en_question
    template_eng['afmt'] = styles.en_answer
    template_ru = collection.models.new_template('ru -> en')
    template_ru['qfmt'] = styles.ru_question
    template_ru['afmt'] = styles.ru_answer
    return template_eng, template_ru


def create_new_model(collection, fields, model_css):
    model = collection.models.new("LinguaLeo_model")
    model['css'] = model_css
    for field in fields:
        collection.models.add_field(model, collection.models.new_field(field))
    template_eng, template_ru = create_templates(collection)
    collection.models.add_template(model, template_eng)
    collection.models.add_template(model, template_ru)
    collection.models.update(model)
    return model


def is_model_exist(collection, fields):
    ll_model = collection.models.by_name('LinguaLeo_model')
    if ll_model:
        ll_fields = set(collection.models.field_names(ll_model))
        return all(f in ll_fields for f in fields)
    return False


def prepare_model(collection, fields, model_css):
    """
    Returns a model for our future notes.
    Creates a deck to keep them.
    """
    if is_model_exist(collection, fields):
        model = collection.models.by_name('LinguaLeo_model')
    else:
        model = create_new_model(collection, fields, model_css)
        # TODO: Move Deck name to config?
        # Create a deck "LinguaLeo" and write id to deck_id
        model['did'] = collection.decks.id('LinguaLeo')
    collection.models.set_current(model)
    collection.models.update(model)
    return model


def send_to_download(word, timeout, retries, sleep_seconds):
    # try to download the picture and the sound the specified number of times,
    # if not succeeded, raise the last error happened to be shown as a problem word
    sound_url = word.get('pronunciation')
    if sound_url and is_valid_ascii(sound_url):
        try_downloading_media(sound_url, timeout, retries, sleep_seconds)

    pic_url = word.get('picture')
    # TODO: Remove or refactor the following code that supports old API
    translations = word.get('translations')
    if translations:
        translation = translations[0]
        if translation.get('pic'):
            pic_url = translation['pic']
    # End of old API code
    if pic_url and not is_default_picture(pic_url):
        if not is_valid_ascii(pic_url):
            raise urllib.error.URLError('Invalid picture url: ' + pic_url)
        try_downloading_media(pic_url, timeout, retries, sleep_seconds)


def try_downloading_media(url, timeout, retries, sleep_seconds):
    exc_happened = None
    for _ in list(range(retries)):
        exc_happened = None
        try:
            download_media_file(url, timeout)
            break
        except (urllib.error.URLError, socket.error) as e:
            exc_happened = e
            time.sleep(sleep_seconds)
    if exc_happened:
        raise exc_happened


def download_media_file(url, timeout):
    destination_folder = mw.col.media.dir()
    name = url.split('/')[-1]
    if is_default_picture(name):
        return
    name = get_valid_name(name)
    abs_path = os.path.join(destination_folder, name)
    if os.path.exists(abs_path):
        # No need to download file again if it already exists
        return
    # Fix '\n' symbols in the url (they were found in the long sentences)
    url = url.replace('\n', '')
    # TODO: find a better way for unsecure connection
    resp = urllib.request.urlopen(url, timeout=timeout, context=ssl._create_unverified_context())
    content = resp.read()
    with open(abs_path, "wb") as media_file:
        media_file.write(content)


def fill_note(word, note):
    note['en'] = word.get('wordValue')
    # print("Filling word {}".format(word['wd']))
    note['ru'] = word.get('combinedTranslation')
    picture_name = word.get('picture').split('/')[-1] if word.get('picture') else ''
    # TODO: Remove old api code when not needed
    translations = word.get('translations')
    if translations:  # translations are used in old API
        # User's choice translation has index 0, then come translations sorted by votes (higher to lower)
        translation = translations[0]
        if translation.get('ctx'):
            note['context'] = translation['ctx']
        if translation.get('pic'):
            picture_name = translation['pic'].split('/')[-1]
    if picture_name and is_valid_ascii(picture_name) and \
            not is_default_picture(picture_name):
        picture_name = get_valid_name(picture_name)
        note['picture_name'] = '<img src="%s" />' % picture_name

    # TODO: Investigate if it is possible to get context differently, since with API 1.0.1
    #  there is no context at the time of getting list of words

    if word.get('transcription'):
        note['transcription'] = '[' + word['transcription'] + ']'
    sound_url = word.get('pronunciation')
    if sound_url:
        sound_name = sound_url.split('/')[-1]
        sound_name = get_valid_name(sound_name)
        note['sound_name'] = '[sound:%s]' % sound_name
    # TODO: Add user dictionaries (wordsets) as tags
    return note


def add_word(word, model):
    word_value = word.get('wordValue')
    if word_value == '':
        return
    collection = mw.col
    note = notes.Note(collection, model)
    note = fill_note(word, note)

    note_dupes = get_duplicates(word_value)

    if not note_dupes:
        collection.addNote(note)
    else:
        for nid in note_dupes:
            note_in_db = notes.Note(collection, id=nid)
            note_in_db['ru'] = note['ru']
            note_in_db['context'] = note['context']
            note_in_db['transcription'] = note['transcription']
            note_in_db['picture_name'] = note['picture_name']
            note_in_db['sound_name'] = note['sound_name']
            note_in_db.flush()
            # TODO: Update tags (user wordsets) when implemented
    # TODO: Check if it is possible to update Anki's media collection to remove old (unused) media


def get_duplicates(word_value):
    # TODO: Use find_dupes instead, but check how quotes and other special symbols are handled
    collection = mw.col
    # escape backslash
    if '\\' in word_value:
        word_value = word_value.replace('\\', '\\\\')
    try:
        # check for sentences or words containing double quotes
        if '"' in word_value:
            if anki_version > 23:
                escaped = word_value.replace('"', '\\"')
                # Note: We can't search for 'en' field when there are escaped double quotes
                note_dupes = collection.find_notes('"%s"' % escaped)
            else:
                # Support Anki < 2.1.24, where searching with single quotes was still allowed
                note_dupes = collection.findNotes("en:'%s'" % word_value)
        else:
            note_dupes = collection.find_notes('en:"%s"' % word_value)
    except InvalidInput:
        # TODO: find a better solution for this fix
        problem = "The word '{}' contains unexpected symbols and it can't be checked for duplicates. " \
                  "Please open an issue on GitHub: https://github.com/vi3itor/lingualeoanki/issues/new".format(word_value)
        showInfo(problem)
        return None

    # TODO: Check why findNotes returns duplicated note ids
    #  there might be a different function to find unique note ids
    # Cast protobuf sequence to list, then exclude duplicates
    return set(list(note_dupes)) if note_dupes else None


def is_duplicate(word_value):
    """
    Check if the word exists in collection
    :param word_value: str
    :return: bool
    """
    if word_value == '':
        return True
    return True if get_duplicates(word_value) else False


def is_valid_ascii(url):
    """
    Check an url if it is a valid ascii string
    After the LinguaLeo update some images
    have broken links with cyrillic characters
    """
    if url == '':
        return True
    try:
        url.encode('ascii')
    except:
        return False
    return True


def is_default_picture(picture_name):
    """
    All words that have no picture link to the same image file.
    We shouldn't download it or fill into the note.
    """
    default_names = [
        '0bbdd3793cb97ec4189557013fc4d6e4bed4f714.png',
        '1611_1361481210.jpg'
    ]
    return picture_name in default_names


def get_valid_name(orig_name):
    """
    Unfortunately, from April 30, 2019,
    media filenames can be very long and contain '\n' symbols,
    the function checks if it is the case
    and returns a name without '\n' and only up to max_length=50 characters
    """
    max_length = 50
    if len(orig_name) > max_length or orig_name.find('\n'):
        new_name = orig_name[-max_length:]
        new_name = new_name.replace('\n', '')
        return new_name
    else:
        return orig_name


def get_module_name():
    return __name__.split(".")[0]


def get_addon_dir():
    root = mw.pm.addonFolder()
    addon_dir = os.path.join(root, get_module_name())
    return addon_dir


def get_cookies_path():
    """
    Returns a full path to cookies.txt in the user_files folder
    :return:
    """
    # user_files folder in the current addon's dir
    uf_dir = os.path.join(get_addon_dir(), 'user_files')
    # Create a folder if doesn't exist
    if not os.path.exists(uf_dir):
        try:
            os.makedirs(uf_dir)
        except:
            # TODO: Improve error handling
            return None
    return os.path.join(uf_dir, 'cookies.txt')


def clean_cookies():
    # TODO: Better handle file removal (check if exists or if in use)
    try:
        os.remove(get_cookies_path())
    except:
        pass


def get_config():
    # Load config from config.json file
    if getattr(getattr(mw, "addonManager", None), "getConfig", None):
        config = mw.addonManager.getConfig(get_module_name())
    else:
        try:
            config_file = os.path.join(get_addon_dir(), 'config.json')
            with open(config_file, 'r') as f:
                config = json.loads(f.read())
        except IOError:
            config = None
    return config


def update_config(config):
    if getattr(getattr(mw, "addonManager", None), "writeConfig", None):
        mw.addonManager.writeConfig(get_module_name(), config)
    else:
        try:
            config_file = os.path.join(get_addon_dir(), 'config.json')
            with open(config_file, 'w') as f:
                json.dump(config, f, sort_keys=True, indent=2)
        except:
            # TODO: Improve error handling
            pass


def get_version_update_notification():
    """
    When a user updates add-on using Anki's built-in add-on manager,
    they need to restart Anki for changes to take effect.
    Loads add-on version from the file and compares with one in the memory.
    If they differ, notify user to restart Anki.
    :return: str with notification message or None
    """
    version_file = os.path.join(get_addon_dir(), '_version.py')
    with open(version_file, 'r') as f:
        if is_newer_version_available(f):
            return 'Please restart Anki to finish updating the Add-on'
    return None


def is_newer_version_available(lines):
    version_prefix = 'VERSION = '
    for line in lines:
        if line.startswith(version_prefix):
            version_in_file = line.split('\'')[-2]
            if version_in_file != VERSION:
                return True
    return False
