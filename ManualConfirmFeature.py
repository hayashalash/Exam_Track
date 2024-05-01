from tkinter import *
from tkinter import Button, ttk, messagebox, scrolledtext
import tkinter as tk

import StudentData
from StudentData import *


class ManualConfirm:

    def __init__(self):
        self.flag_other_reason = None
        self.str_reason = None

    # Manual confirm Window
    def confirm_popup(self, parent, student_id):
        if len(student_id) == 0:
            return
        confirm_window = Toplevel(parent)
        confirm_window.geometry("300x320+350+100")
        confirm_window.resizable(False, False)
        confirm_window.title("Manual Confirm")
        confirm_window.configure(bg='#917FB3')

        confirm_window_reason = Label(confirm_window, text="Select Reason:",
                                      bg='#917FB3', font=("Calibri", 16 * -1))
        confirm_window_reason.place(x=30, y=70)

        confirm_window_id = Label(confirm_window, text="Student ID:",
                                  bg='#917FB3', font=("Calibri", 16 * -1))
        confirm_window_id.place(x=30, y=30)
        confirm_window_id2 = Label(confirm_window, text=student_id, bg='#917FB3', font=("Calibri", 16 * -1),
                                   borderwidth=1, relief="groove")
        confirm_window_id2.place(x=120, y=30)

        confirm_window_text_area = scrolledtext.ScrolledText(confirm_window, wrap=tk.WORD, bd=3, background="#E5BEEC",
                                                             width=25, height=3, font=("Calibri", 16 * -1))

        confirm_window_specify = Label(confirm_window, text="Please specify:",
                                       bg='#917FB3', font=("Calibri", 16 * -1))

        self.str_reason = ""
        self.flag_other_reason = 0

        def manual_confirm_submit(s_student_id):
            if self.flag_other_reason != 0:
                self.str_reason = confirm_window_text_area.get("1.0", END).strip()
            if len(self.str_reason) < 3:
                messagebox.showerror("Manual Confirm Error", "Invalid Reason", parent=confirm_window)
            else:
                res = students.student_manual_confirm_attendance(s_student_id, self.str_reason)
                if res == STUDENT_ALREADY_CONFIRMED:
                    messagebox.showerror("Manual Confirm Error", "Student Already Confirmed", parent=confirm_window)
                confirm_window.destroy()

        # Buttons
        w_confirm_btn = Button(confirm_window, text='Confirm', bd='5', fg="#FFFFFF", bg='#812e91',
                               font=("Calibri", 14 * -1), activebackground='#917FB3', height='1', width='12',
                               disabledforeground='gray', command=lambda: manual_confirm_submit(student_id))
        w_confirm_btn.place(x=30, y=250)

        w_cancel_btn = Button(confirm_window, text='Cancel', bd='5', fg="#FFFFFF", bg='#812e91',
                              font=("Calibri", 14 * -1), activebackground='#917FB3', height='1', width='12',
                              disabledforeground='gray', command=confirm_window.destroy)
        w_cancel_btn.place(x=145, y=250)

        # Combobox functionality
        def reasons_combo_changed(event):
            selected_reason = combo_reasons.get()

            if selected_reason == 'Other':
                confirm_window_text_area.configure(state='normal')
                confirm_window_specify.place(x=30, y=140)
                confirm_window_text_area.place(x=30, y=170)
                self.flag_other_reason = 1
            else:
                confirm_window_text_area.place_forget()
                confirm_window_specify.place_forget()
                self.flag_other_reason = 0
                self.str_reason = selected_reason

        reason_list = [StudentData.ManualConfirmReason.FACEREC.value, StudentData.ManualConfirmReason.PIC.value,
                       StudentData.ManualConfirmReason.TIME.value, StudentData.ManualConfirmReason.OTHER.value]

        combo_reasons = ttk.Combobox(confirm_window, state="readonly", values=reason_list,
                                     background="gray", font=("Calibri", 16 * -1))
        combo_reasons.place(x=30, y=110)

        combo_reasons.bind("<<ComboboxSelected>>", reasons_combo_changed)
