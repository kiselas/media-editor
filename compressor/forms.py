from django import forms

from django_media_editor.constants import (
    AVAILABLE_IMAGE_FORMATS,
    AVAILABLE_VIDEO_FORMATS,
    IMAGE_CONVERTER_CHOICES,
    VIDEO_CONVERTER_CHOICES,
    VIDEO_QUANTIZE_CHOICES,
)


class ConvertVideoForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={"class": "dropzone",
                                                         "accept": ",".join(AVAILABLE_VIDEO_FORMATS)}),
                           label=False)
    convert_format = forms.ChoiceField(choices=VIDEO_CONVERTER_CHOICES,
                                       widget=forms.Select(attrs={"class": "converter-choices"}),
                                       label="Выберите формат для конвертации")


class ConvertImageForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={"class": "dropzone",
                                                         "accept": ",".join(AVAILABLE_IMAGE_FORMATS)}),
                           label=False)
    convert_format = forms.ChoiceField(choices=IMAGE_CONVERTER_CHOICES,
                                       widget=forms.Select(attrs={"class": "converter-choices"}),
                                       label="Выберите формат для конвертации")


class CompressVideoForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={"class": "dropzone",
                                                         "accept": ",".join(AVAILABLE_VIDEO_FORMATS)}),
                           label=False)
    compression_ratio = forms.CharField(widget=forms.TextInput(
        attrs={"type": "range",
               "class": "form-range",
               "min": "0",
               "max": "5",
               "value": "1",
               }), label="Степень сжатия")


class UploadImageForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={"class": "dropzone",
                                                         "accept": ",".join(AVAILABLE_IMAGE_FORMATS)}),
                           label=False)
    compression_ratio = forms.CharField(widget=forms.TextInput(
        attrs={"type": "range",
               "class": "form-range",
               "min": "10",
               "max": "90",
               "value": "40",
               "step": "10",
               }), label="Степень сжатия")


class ConvertVideoToGifForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={"class": "dropzone",
                                                         "accept": ",".join(AVAILABLE_VIDEO_FORMATS)}),
                           label=False)
    start_time = forms.CharField(widget=forms.TextInput(attrs={"class": "converter-choices"}),
                                 label="Укажите время начала (в секундах)")
    end_time = forms.CharField(widget=forms.TextInput(attrs={"class": "converter-choices"}),
                               label="Укажите время конца (в секундах)")
    quantize_algorithm = forms.ChoiceField(choices=VIDEO_QUANTIZE_CHOICES,
                                        widget=forms.Select(attrs={"class": "converter-choices"}),
                                        label="Выберете алгоритм квантизации. Можно оставить значение по-умолчанию."
                                              "\n(Попробуйте изменить алгоритм, если есть артефакты в "
                                              "цветах gif-картинки)")
