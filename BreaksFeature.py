from tkinter import *
from tkinter import Button, ttk, messagebox,scrolledtext
import tkinter as tk
from StudentData import *


class BreaksFeature:

    def __init__(self):
        self.flag_other_reason = None
        self.str_reason = None

    def break_window(self, parent, student_id):
        if len(student_id) == 0:
            return

        break_window = Toplevel(parent)
        break_window.geometry("300x320+350+100")
        break_window.resizable(False,False)
        break_window.title("Student Break")
        break_window.configure(bg='#917FB3')

        break_window_reason =  Label(break_window, text="Select Reason:" ,bg='#917FB3',font=("Calibri", 16 * -1))
        break_window_reason.place(x=30,y=70)

        break_window_id = Label(break_window, text="Student ID:" ,bg='#917FB3',font=("Calibri", 16 * -1))
        break_window_id.place(x=30,y=30)
        break_window_id2 = Label(break_window, text=student_id ,bg='#917FB3',font=("Calibri", 16 * -1),
                                           borderwidth=1, relief="groove")
        break_window_id2.place(x=120,y=30)

        break_window_text_area = scrolledtext.ScrolledText(break_window, wrap=tk.WORD,bd=3,background="#E5BEEC",
                                  width=25, height=3,font=("Calibri", 16*-1))

        break_window_specify = Label(break_window, text="Please specify:" ,
                                       bg='#917FB3',font=("Calibri", 16 * -1))

        self.str_reason = ""
        self.flag_other_reason = 0

        def break_submit(s_student_id):
            if self.flag_other_reason != 0:
                self.str_reason = break_window_text_area.get("1.0",END).strip()
            if len(self.str_reason) < 3:
                messagebox.showerror("Break Error", "Invalid Reason.",parent=break_window)
            else:
                res = students.student_report_break(s_student_id,self.str_reason)
                if res == STUDENT_NOT_FOUND:
                    messagebox.showerror("Break Error", "Student not found.", parent=break_window)
                elif res == STUDENT_ALREADY_ON_BREAK:
                    messagebox.showerror("Break Error", "Student already on break.", parent=break_window)
                break_window.destroy()
            return FUNC_SUCCESS

        # Buttons
        break_confirm_btn = Button(break_window, text='Confirm', bd='5',fg="#FFFFFF" ,bg='#812e91',
                                  font=("Calibri", 14 * -1),activebackground='#917FB3',height='1',width='12',
                                  disabledforeground='gray',command=lambda: break_submit(student_id))
        break_confirm_btn.place(x = 30, y= 250)

        break_cancel_btn = Button(break_window, text='Cancel', bd='5',fg="#FFFFFF" ,bg='#812e91',
                                 font=("Calibri", 14 * -1),activebackground='#917FB3',height='1',width='12',
                                 disabledforeground='gray',command=break_window.destroy)
        break_cancel_btn.place(x = 145, y= 250)

        # Combobox functionality
        def reasons_combo_changed(event):
            selected_reason = combo_reasons.get()

            if selected_reason == 'Other':
                break_window_text_area.configure(state='normal')
                break_window_specify.place(x=30,y=140)
                break_window_text_area.place(x=30,y=170)
                self.flag_other_reason = 1
            else:
                break_window_text_area.place_forget()
                break_window_specify.place_forget()
                self.flag_other_reason = 0
                self.str_reason = selected_reason

        reason_list = ['Restroom', 'Medical', 'Other']

        combo_reasons = ttk.Combobox(break_window, state="readonly" , values=reason_list,
                                   background="gray",font=("Calibri", 16 * -1))
        combo_reasons.place(x=30,y=110)

        combo_reasons.bind("<<ComboboxSelected>>", reasons_combo_changed)

    # view window
    def view_break_window(self, parent, student_id):
        if len(student_id) == 0:
            return
        if not students.student_had_break(student_id):
            return

        view_break_window = Toplevel(parent)
        view_break_window.geometry("500x370+350+100")
        view_break_window.resizable(False,False)
        view_break_window.title("Student Breaks")
        view_break_window.configure(bg='#917FB3')

        view_break_window_id = Label(view_break_window, text="Student ID:" ,bg='#917FB3',font=("Calibri", 16 * -1))
        view_break_window_id.place(x=30,y=30)
        view_break_window_id2 = Label(view_break_window, text=student_id ,bg='#917FB3',font=("Calibri", 16 * -1),
                                           borderwidth=1, relief="groove")
        view_break_window_id2.place(x=120,y=30)

        view_total_breaks = Label(view_break_window, text="Total Breaks: " + str(students.student_total_breaks(student_id)),
                                  bg='#917FB3',font=("Calibri", 16 * -1))

        view_total_breaks.place(x=30,y=60)

        total_time = divmod(students.student_total_break_time(student_id), 60)
        total_time_string = 'Total Break time:  ' + str(int(total_time[0])) + ' minutes ' + str(int(total_time[1])) + ' seconds'

        view_total_time = Label(view_break_window, text=total_time_string,
                                  bg='#917FB3',font=("Calibri", 16 * -1))

        view_total_time.place(x=30,y=90)

        # creating table
        cols = ['Reason', 'Length']
        table = ttk.Treeview(master=view_break_window, columns=cols, show="headings")

        table.tag_configure('oddrow', background='#917FB3')
        table.tag_configure('evenrow', background='#BAA4CA')

        for column in cols:
            table.heading(column=column, text=column)
            if column == 'Reason':
                table.column(column=column, width=270)
            else:
                table.column(column=column, width=155)

        color_j = 0
        for i in range(0,students.students_breaks[student_id][0]):

            if i == (students.students_breaks[student_id][0]-1) \
                    and len(students.students_breaks[student_id][1]) < students.students_breaks[student_id][0]:
                row_data = [students.students_breaks[student_id][2][i], 'Ongoing']
            else:
                break_time_i = students.students_breaks[student_id][1][i]
                total_time_i = divmod(break_time_i, 60)
                row_data = [students.students_breaks[student_id][2][i],
                            str(int(total_time_i[0])) + ' minutes ' + str(int(total_time_i[1])) + ' seconds']
            color_tags = ('evenrow',) if color_j % 2 == 0 else ('oddrow',)
            table.insert(parent="", index="end", values=row_data, tags=color_tags)
            color_j += 1

        table.place(x=30, y=120, height=170)

        view_break_done_btn = Button(view_break_window, text='Done', bd='5',fg="#FFFFFF" ,bg='#812e91'
                                    ,font=("Calibri", 16 * -1),activebackground='#917FB3',height='1',
                                    width='14', disabledforeground='gray',command = view_break_window.destroy)
        view_break_done_btn.place(x = 330, y= 310)




