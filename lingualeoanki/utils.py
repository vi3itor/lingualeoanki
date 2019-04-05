import os
from random import randint
import json
from .six.moves import urllib
import socket

from aqt import mw
from anki import notes

from . import styles
from ._name import ADDON_NAME


fields = ['en', 'transcription',
          'ru', 'picture_name',
          'sound_name', 'context']


def create_templates(collection):
    template_eng = collection.models.newTemplate('en -> ru')
    template_eng['qfmt'] = styles.en_question
    template_eng['afmt'] = styles.en_answer
    template_ru = collection.models.newTemplate('ru -> en')
    template_ru['qfmt'] = styles.ru_question
    template_ru['afmt'] = styles.ru_answer
    return (template_eng, template_ru)


def create_new_model(collection, fields, model_css):
    model = collection.models.new("LinguaLeo_model")
    model['tags'].append("LinguaLeo")
    model['css'] = model_css
    for field in fields:
        collection.models.addField(model, collection.models.newField(field))
    template_eng, template_ru = create_templates(collection)
    collection.models.addTemplate(model, template_eng)
    collection.models.addTemplate(model, template_ru)
    model['id'] = randint(100000, 1000000)  # Essential for upgrade detection
    collection.models.update(model)
    return model


def is_model_exist(collection, fields):
    name_exist = 'LinguaLeo_model' in collection.models.allNames()
    if name_exist:
        fields_ok = collection.models.fieldNames(collection.models.byName(
                                                'LinguaLeo_model')) == fields
    else:
        fields_ok = False
    return (name_exist and fields_ok)


def prepare_model(collection, fields, model_css):
    """
    Returns a model for our future notes.
    Creates a deck to keep them.
    """
    if is_model_exist(collection, fields):
        model = collection.models.byName('LinguaLeo_model')
    else:
        model = create_new_model(collection, fields, model_css)
    # Create a deck "LinguaLeo" and write id to deck_id
    model['did'] = collection.decks.id('LinguaLeo')
    collection.models.setCurrent(model)
    collection.models.save(model)
    return model


def download_media_file(url):
    DOWNLOAD_TIMEOUT = 20
    destination_folder = mw.col.media.dir()
    name = url.split('/')[-1]
    abs_path = os.path.join(destination_folder, name)
    resp = urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT)
    media_file = resp.read()
    # TODO: Handle exceptions of writing to file
    with open(abs_path, "wb") as binfile:
        binfile.write(media_file)


def send_to_download(word, thread):
    # TODO: Move to config following settings
    NUM_RETRIES = 5
    SLEEP_SECONDS = 5
    # try to download the picture and the sound the specified number of times,
    # if not succeeded, raise the last error happened to be shown as a problem word
    picture_url = word.get('picture_url')
    if picture_url:
        exc_happened = None
        picture_url = 'http:' + picture_url
        for i in list(range(NUM_RETRIES)):
            exc_happened = None
            try:
                download_media_file(picture_url)
                break
            except (urllib.error.URLError, socket.error) as e:
                exc_happened = e
                thread.sleep(SLEEP_SECONDS)
        if exc_happened:
            raise exc_happened
    sound_url = word.get('sound_url')
    if sound_url:
        exc_happened = None
        for i in list(range(NUM_RETRIES)):
            exc_happened = None
            try:
                download_media_file(sound_url)
                break
            except (urllib.error.URLError, socket.error) as e:
                exc_happened = e
                thread.sleep(SLEEP_SECONDS)
        if exc_happened:
            raise exc_happened


def fill_note(word, note):
    note['en'] = word['word_value']
    note['ru'] = word['user_translates'][0]['translate_value']
    if word.get('transcription'):
        note['transcription'] = '[' + word.get('transcription') + ']'
    if word.get('context'):
        note['context'] = word.get('context')
    picture_url = word.get('picture_url')
    if picture_url:
        picture_name = picture_url.split('/')[-1]
        note['picture_name'] = '<img src="%s" />' % picture_name
    sound_url = word.get('sound_url')
    if sound_url:
        sound_name = sound_url.split('/')[-1]
        note['sound_name'] = '[sound:%s]' % sound_name
    return note


def add_word(word, model):
    # TODO: Introduce new fields to the model (pic_url and sound_url)
    #  for testing if update is needed and implement a function
    #  to update existing models (to introduce new fields) for compatibility
    collection = mw.col
    note = notes.Note(collection, model)
    note = fill_note(word, note)
    # TODO: Rewrite and use is_duplicate()
    dupes = collection.findDupes("en", word['word_value'])
    # a hack to support words with apostrophes
    note_dupes1 = collection.findNotes("en:'%s'" % word['word_value'])
    note_dupes2 = collection.findNotes('en:"%s"' % word['word_value'])
    note_dupes = note_dupes1 + note_dupes2
    if not dupes and not note_dupes:
        collection.addNote(note)
    elif (note['picture_name'] or note['sound_name']) and note_dupes:
        # update existing notes with new pictures and sounds in case
        # they have been changed in LinguaLeo's UI
        for nid in note_dupes:
            note_in_db = notes.Note(collection, id=nid)
            # a dirty hack below until a new field in the model is introduced
            # put a space before or after a *sound* field of an existing note if you want it to be updated
            # if a note has no picture or sound, it will be updated anyway
            sound_name = note_in_db['sound_name']
            sound_name = sound_name.replace("&nbsp;", " ")
            note_needs_update = sound_name != sound_name.strip()
            if note['picture_name'] and (note_needs_update or not note_in_db['picture_name'].strip()):
                note_in_db['picture_name'] = note['picture_name']
            if note['sound_name'] and (note_needs_update or not note_in_db['sound_name'].strip()):
                note_in_db['sound_name'] = note['sound_name']
            note_in_db.flush()
    # TODO: Check if it is possible to update Anki's media collection to remove old (unused) media


def is_duplicate(word):
    """
    Check if the word exists in collection
    :param word: dictionary
    :return: bool
    """
    collection = mw.col
    dupes = collection.findDupes("en", word['word_value'])
    # a hack to support words with apostrophes
    # TODO: Debug to find out if it is still required
    note_dupes1 = collection.findNotes("en:'%s'" % word['word_value'])
    note_dupes2 = collection.findNotes('en:"%s"' % word['word_value'])
    note_dupes = note_dupes1 + note_dupes2
    return True if dupes or note_dupes else False


def get_addon_dir():
    root = mw.pm.addonFolder()
    addon_dir = os.path.join(root, ADDON_NAME)
    return addon_dir


def get_cookies_path():
    """
    Returns a full path to cookies.txt in the user_files folder
    :return:
    """
    root = mw.pm.addonFolder()
    # user_files folder in the current addon's dir
    uf_dir = os.path.join(root, ADDON_NAME, 'user_files')
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
        config = mw.addonManager.getConfig(ADDON_NAME)
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
        mw.addonManager.writeConfig(ADDON_NAME, config)
    else:
        try:
            config_file = os.path.join(get_addon_dir(), 'config.json')
            with open(config_file, 'w') as f:
                json.dump(config, f, sort_keys=True, indent=2)
        except:
            # TODO: Improve error handling
            pass
