import os
from random import randint
from urllib2 import urlopen

fields = ['en', 'transcription', 'ru', 'picture_name', 'sound_name', 'context']
model_css = '.card {font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white;} .from {font-style: italic;}'
# # Html for templates
# en_question = '<strong>{{en}}</strong><br><br>[{{transcription}}]<br><br>{{picture_name}}<br><br>{{sound_name}}'
# en_answer = '{{FrontSide}}<hr id=answer><font color="#0000ff">{{ru}}</font><br><br><em>{{context}}</em>'
# ru_question = '{{ru}}<br><br>{{picture_name}}<br><br>{{type:en}}'
# ru_answer = '{{FrontSide}}<hr id=answer><strong><font color="#0000ff"></font></strong><br>[{{transcription}}]<br>{{sound_name}}<br><em>{{context}}</em>'

def create_templates(collection):
    ''' Returns 2 templates (eng - ru and ru - eng) with 2 sides, front('qfmt') and back('afmt') '''    
    template_eng = collection.models.newTemplate('en -> ru')
    template_eng['qfmt'] = '''<strong>{{en}}</strong><br><br>{{transcription}}<br><br>{{picture_name}}<br><br>{{sound_name}}'''                        
    template_eng['afmt'] = '''{{FrontSide}}<hr id=answer><font color="#0000ff">{{ru}}</font><br><br><em>{{context}}</em>'''
    template_ru = collection.models.newTemplate('ru -> en')
    template_ru['qfmt'] = '''{{ru}}<br><br>{{picture_name}}<br><br>{{type:en}}'''
    template_ru['afmt'] = '''{{FrontSide}}<hr id=answer><strong><font color="#0000ff"></font></strong><br>{{transcription}}<br>{{sound_name}}<br><em>{{context}}</em>'''
    return (template_eng, template_ru)

def create_new_model(collection, fields, model_css):
    ''' Create a model for our notes, templates and cards '''
    model = collection.models.new("LinguaLeo_model")
    model['tags'].append("LinguaLeo")    
    model['css'] = model_css
    for field in fields:
        collection.models.addField(model, collection.models.newField(field))       
    template_eng, template_ru = create_templates(collection)
    collection.models.addTemplate(model, template_eng)
    collection.models.addTemplate(model, template_ru)    
    model['id'] = randint(100000, 1000000) # Essential for upgrade detection
    collection.models.update(model)
    return model

def is_model_exist(collection, fields):
    name_exist = 'LinguaLeo_model' in collection.models.allNames()
    if name_exist:        
        fields_ok = collection.models.fieldNames(collection.models.byName('LinguaLeo_model')) == fields
    else: 
        fields_ok = False
    return (name_exist and fields_ok)
    
def prepare_model(collection, fields, model_css):
    ''' Returns a model for our future notes. Creates a deck to keep them. '''
    if is_model_exist(collection, fields):
        model = collection.models.byName('LinguaLeo_model')
    else:    
        model = create_new_model(collection, fields, model_css)
    # Create a deck "LinguaLeo" and write id to deck_id 
    model['did'] = collection.decks.id('LinguaLeo') 
    collection.models.setCurrent(model)
    collection.models.save(model)
    return model 
    
def download_media_file(destination_folder, url):
    name = url.split('/')[-1]
    abs_path = os.path.join(destination_folder, name)
    resp = urlopen(url)
    media_file = resp.read()
    binfile = open(abs_path, "wb")
    binfile.write(media_file)
    binfile.close()
    
def send_to_download(word, destination_folder):
    picture_url = word.get('picture_url')
    if picture_url:
        picture_url = 'http:' + picture_url
        download_media_file(destination_folder, picture_url)
    sound_url = word.get('sound_url')
    if sound_url:
        download_media_file(destination_folder, sound_url) 
 
def fill_note(word, note, destination_folder):
    note['en'] = word['word_value']
    note['ru'] = word['user_translates'][0]['translate_value']   
    if word.get('transcription'):
        note['transcription'] = '[' + word.get('transcription') + ']' # TEST IT
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
 