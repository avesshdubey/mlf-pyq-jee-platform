import fitz
import os
import re
import asyncio
import winrt.windows.media.ocr as win_ocr
import winrt.windows.graphics.imaging as win_imaging
import winrt.windows.storage as win_storage

async def ocr_page(doc, pno):
    pix = doc[pno].get_pixmap(dpi=150)
    temp_img = f"temp_sc_{pno}.png"
    pix.save(temp_img)
    f_obj = await win_storage.StorageFile.get_file_from_path_async(os.path.abspath(temp_img))
    stream = await f_obj.open_async(win_storage.FileAccessMode.READ)
    decoder = await win_imaging.BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    engine = win_ocr.OcrEngine.try_create_from_user_profile_languages()
    res = await engine.recognize_async(bitmap)
    os.remove(temp_img)
    return res.text

async def main():
    doc = fitz.open(r"C:\Users\avesh\Desktop\PYQS\PDF_COM_202611031249451070.pdf")
    print(f"Total pages in PDF_COM: {len(doc)}")
    for p in [0, 4, 8, 12]:
        text = await ocr_page(doc, p)
        print(f"=== Page {p+1} ===")
        # Look for question number, question text, options, correct answer
        print(text[:400].replace('\n', ' '))
    doc.close()

asyncio.run(main())
