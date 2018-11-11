import os
from random import randint
import socket
import urllib2
import time

from aqt import mw
from anki import notes

from lingualeo import styles


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
    resp = urllib2.urlopen(url, timeout=DOWNLOAD_TIMEOUT)
    media_file = resp.read()
    binfile = open(abs_path, "wb")
    binfile.write(media_file)
    binfile.close()


def send_to_download(word, thread):
    NUM_RETRIES = 5
    SLEEP_SECONDS = 5
    # try to download the picture and the sound the specified number of times,
    # if not succeeded, raise the last error happened to be shown as a problem word
    picture_url = word.get('picture_url')
    if picture_url:
        exc_happened = None
        picture_url = 'http:' + picture_url
        for i in xrange(NUM_RETRIES):
            exc_happened = None
            try:
                download_media_file(picture_url)
                break
            except (urllib2.URLError, socket.error) as e:
                thread.sleep(SLEEP_SECONDS)
        if exc_happened:
            raise
    sound_url = word.get('sound_url')
    if sound_url:
        exc_happened = None
        for i in xrange(NUM_RETRIES):
            exc_happened = None
            try:
                download_media_file(sound_url)
                break
            except (urllib2.URLError, socket.error) as e:
                exc_happened = e
                thread.sleep(SLEEP_SECONDS)
        if exc_happened:
            raise


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
    collection = mw.col
    note = notes.Note(collection, model)
    note = fill_note(word, note)
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


# my adds
def get_the_last_word():
    # mid - id deck
    # one should determine mid after second and next uploading data
    # to upload correctly to the deck
    m = mw.col.models.byName("LinguaLeo_model")
    mid = m['id']
    last_word = mw.col.db.execute("SELECT sfld FROM notes WHERE mid = " + str(mid) + " ORDER BY id DESC LIMIT 1")
    for row in last_word:
        last = row
    return last[0]