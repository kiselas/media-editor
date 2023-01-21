from django import forms

from django_media_editor.constants import AVAILABLE_VIDEO_FORMATS, AVAILABLE_IMAGE_FORMATS, VIDEO_CONVERTER_CHOICES, \
    IMAGE_CONVERTER_CHOICES


class ConvertVideoForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'dropzone',
                                                         'accept': ','.join(AVAILABLE_VIDEO_FORMATS)}),
                           label=False)
    convert_format = forms.ChoiceField(choices=VIDEO_CONVERTER_CHOICES,
                                          widget=forms.Select(attrs={'class': 'converter-choices'}),
                                          label='Выберите формат для конвертации')


class ConvertImageForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'dropzone',
                                                         'accept': ','.join(AVAILABLE_IMAGE_FORMATS)}),
                           label=False)
    convert_format = forms.ChoiceField(choices=IMAGE_CONVERTER_CHOICES,
                                          widget=forms.Select(attrs={'class': 'converter-choices'}),
                                          label='Выберите формат для конвертации')


class CompressVideoForm(forms.Form):
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
