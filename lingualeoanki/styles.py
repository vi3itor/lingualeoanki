model_css = '''
    .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color:
        white;
        }
    .from {
        font-style: italic;
    }'''

# TODO: think about doing one-time check and suggesting existing users to update the style:
#   because the picture was moved to the answer side
en_question = """
    <strong>{{en}}</strong>
    <br><br>
    {{transcription}}
    <br><br>
    {{sound_name}}
    """

en_answer = """
    {{FrontSide}}
    <hr id=answer>
    <font color="#0000ff">{{ru}}</font>
    <br><br>
    {{picture_name}}
    <br><br>
    <em>{{context}}</em>
    """

ru_question = """
    {{ru}}
    <br><br>
    """

ru_answer = """
    {{FrontSide}}
    <hr id=answer>
    {{en}}
    <br>
    {{transcription}}
    <br>
    {{sound_name}}
    <br>
    {{picture_name}}
    <br><br>
    <em>{{context}}</em>
    """
