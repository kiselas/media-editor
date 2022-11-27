from django import forms

from compressor.constants import AVAILABLE_VIDEO_FORMATS


class UploadFileForm(forms.Form):
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
