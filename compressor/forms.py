from django import forms

from django_media_editor.constants import AVAILABLE_VIDEO_FORMATS, AVAILABLE_IMAGE_FORMATS


class UploadVideoForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'dropzone',
                                                         'accept': ','.join(AVAILABLE_VIDEO_FORMATS)}),
                           label=False)
    compression_ratio = forms.CharField(widget=forms.TextInput(
        attrs={'type': 'range',
               'class': 'form-range',
               'min': "0",
               'max': "5",
               'value': "1",
               }), label='Степень сжатия')


class UploadImageForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'dropzone',
                                                         'accept': ','.join(AVAILABLE_IMAGE_FORMATS)}),
                           label=False)
    compression_ratio = forms.CharField(widget=forms.TextInput(
        attrs={'type': 'range',
               'class': 'form-range',
               'min': '10',
               'max': '90',
               'value': '60',
               'step': '10',
               }), label='Степень сжатия')
