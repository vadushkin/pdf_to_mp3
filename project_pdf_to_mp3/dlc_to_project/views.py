from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from gtts import gTTS
from pdfminer.pdfparser import PDFSyntaxError
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from django.core.files.storage import FileSystemStorage
import gtts.lang
import io
import datetime


def extract_text_from_pdf(pdf_path):
    """Convert pdf file to text"""
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open('media/' + pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()

    if text:
        return text


def index(request):
    """Main function"""
    list_lg = gtts.lang.tts_langs().keys()
    title = 'pdf to mp3'
    if request.method == 'POST':
        try:
            my_file = request.FILES['my_file']
            my_lg = request.POST['lng']
            fs = FileSystemStorage()
            filename = fs.save(my_file.name, my_file)
            text_val = extract_text_from_pdf(filename)
            try:
                obj = gTTS(text=text_val, lang=my_lg)
                today = datetime.datetime.today()
                time = today.strftime('%Y_%m_%d-%H_%M_%S')
                obj.save(f"mp3/{time}.mp3")
                context = {
                    'title': title,
                    'list_lg': list_lg,
                }
                return render(request, 'dlc_to_project/index.html', context=context)
            except Exception:
                return redirect('home')
        except PDFSyntaxError:
            context = {
                'title': title,
                'list_lg': list_lg,
                'message': 'Укажите pdf file',
            }
            return render(request, 'dlc_to_project/index.html', context=context)
        except MultiValueDictKeyError or PDFSyntaxError:
            context = {
                'title': title,
                'list_lg': list_lg,
                'message': 'Укажите pdf file',
            }
            return render(request, 'dlc_to_project/index.html', context=context)
    context = {
        'title': title,
        'list_lg': list_lg,
    }
    return render(request, 'dlc_to_project/index.html', context=context)
