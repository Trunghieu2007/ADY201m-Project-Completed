import os
import sys

def convert_to_pdf():
    """Chuyển đổi file DOCX sang PDF bằng Word COM Automation."""
    base = os.path.dirname(os.path.abspath(__file__))
    docx_p = os.path.join(base, "Final_Report.docx")
    pdf_p = os.path.join(base, "Final_Report.pdf")
    
    try:
        from docx2pdf import convert
        convert(docx_p, pdf_p)
        print(f"[+] Chuyển đổi thành công docx2pdf: {os.path.exists(pdf_p)} ({os.path.getsize(pdf_p)} bytes)")
        return
    except Exception as e:
        print(f"[-] docx2pdf không khả dụng: {e}")
        
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(docx_p)
        doc.SaveAs(pdf_p, FileFormat=17) # wdFormatPDF
        doc.Close()
        word.Quit()
        print(f"[+] Chuyển đổi thành công qua win32com: {os.path.exists(pdf_p)} ({os.path.getsize(pdf_p)} bytes)")
    except Exception as e:
        print(f"[-] win32com thất bại: {e}")

if __name__ == "__main__":
    convert_to_pdf()
